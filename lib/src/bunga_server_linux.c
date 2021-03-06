/*
 * The MIT License (MIT)
 *
 * Copyright (c) 2020, Erik Moqvist
 *
 * Permission is hereby granted, free of charge, to any person
 * obtaining a copy of this software and associated documentation
 * files (the "Software"), to deal in the Software without
 * restriction, including without limitation the rights to use, copy,
 * modify, merge, publish, distribute, sublicense, and/or sell copies
 * of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
 * BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
 * ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
 * CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 * This file is part of the Monolinux project.
 */

#define _GNU_SOURCE

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/eventfd.h>
#include <pthread.h>
#include <sys/epoll.h>
#include <sys/stat.h>
#include "bunga_server.h"
#include "ml/ml.h"

/**
 * The maximum message size to receive.
 */
#ifndef BUNGA_MESSAGE_SIZE_MAX
#    define BUNGA_MESSAGE_SIZE_MAX                    512
#endif

/**
 * Put file window size.
 */
#ifndef BUNGA_PUT_FILE_WINDOW_SIZE
#    define BUNGA_PUT_FILE_WINDOW_SIZE                100
#endif

/**
 * Get file window size.
 */
#ifndef BUNGA_GET_FILE_WINDOW_SIZE
#    define BUNGA_GET_FILE_WINDOW_SIZE                100
#endif

struct execute_command_t {
    char *command_p;
    int res;
    struct {
        char *buf_p;
        size_t size;
    } output;
    struct {
        struct bunga_server_t *server_p;
        struct bunga_server_client_t *client_p;
    } bunga;
    struct ml_queue_t *queue_p;
};

struct client_t {
    struct bunga_server_client_t *client_p;
    int log_fd;
    FILE *fput_p;
    FILE *fget_p;
    uint32_t outstanding_responses;
    uint32_t window_size;
};

static struct bunga_server_client_t bunga_clients[2];
static struct client_t clients[2];
static struct ml_queue_t queue;
static int epoll_fd;
static uint8_t clients_input_buffers[2][BUNGA_MESSAGE_SIZE_MAX];
static uint8_t message[BUNGA_MESSAGE_SIZE_MAX];
static uint8_t workspace_in[BUNGA_MESSAGE_SIZE_MAX + 64];
static uint8_t workspace_out[BUNGA_MESSAGE_SIZE_MAX + 64];

static ML_UID(uid_execute_command_complete);

static struct client_t *client_from_bunga_client(
    struct bunga_server_client_t *client_p)
{
    return (&clients[client_p - &bunga_clients[0]]);
}

static struct bunga_server_client_t *client_to_bunga_client(
    struct client_t *client_p)
{
    return (&bunga_clients[client_p - &clients[0]]);
}

static void client_init(struct client_t *self_p)
{
    self_p->log_fd = -1;
    self_p->fget_p = NULL;
    self_p->fput_p = NULL;
}

static void client_destroy(struct client_t *self_p)
{
    if (self_p->log_fd != -1) {
        epoll_ctl(epoll_fd, EPOLL_CTL_DEL, self_p->log_fd, NULL);
        close(self_p->log_fd);
        self_p->log_fd = -1;
    }

    if (self_p->fget_p != NULL) {
        fclose(self_p->fget_p);
        self_p->fget_p = NULL;
    }

    if (self_p->fput_p != NULL) {
        fclose(self_p->fput_p);
        self_p->fput_p = NULL;
    }
}

static void client_on_connected(struct client_t *self_p)
{
    struct epoll_event event;

    self_p->log_fd = open("/dev/kmsg", O_RDONLY | O_NONBLOCK);

    if (self_p->log_fd != -1) {
        event.data.fd = self_p->log_fd;
        event.events = EPOLLIN;
        epoll_ctl(epoll_fd, EPOLL_CTL_ADD, self_p->log_fd, &event);
    }
}

static void on_client_connected(struct bunga_server_t *self_p,
                                struct bunga_server_client_t *client_p)
{
    (void)self_p;

    client_on_connected(client_from_bunga_client(client_p));
}

static void on_client_disconnected(struct bunga_server_t *self_p,
                                   struct bunga_server_client_t *client_p)
{
    (void)self_p;

    client_destroy(client_from_bunga_client(client_p));
}

static void execute_command_job(struct execute_command_t *command_p)
{
    FILE *fout_p;

    fout_p = open_memstream(&command_p->output.buf_p, &command_p->output.size);

    if (fout_p != NULL) {
        command_p->res = ml_shell_execute_command(command_p->command_p, fout_p);
        fclose(fout_p);
    } else {
        command_p->output.buf_p = NULL;
        command_p->output.size = 0;
        command_p->res = -ENOMEM;
    }

    ml_queue_put(command_p->queue_p, command_p);
}

static void on_connect_req(struct bunga_server_t *self_p,
                           struct bunga_server_client_t *client_p,
                           struct bunga_connect_req_t *request_p)
{
    (void)client_p;
    (void)request_p;

    struct bunga_connect_rsp_t *response_p;

    response_p = bunga_server_init_connect_rsp(self_p);
    response_p->keep_alive_timeout = 2;
    response_p->maximum_message_size = BUNGA_MESSAGE_SIZE_MAX;
    bunga_server_reply(self_p);
}

static void on_execute_command_req(struct bunga_server_t *self_p,
                                   struct bunga_server_client_t *client_p,
                                   struct bunga_execute_command_req_t *request_p)
{
    struct execute_command_t *command_p;

    command_p = ml_message_alloc(&uid_execute_command_complete, sizeof(*command_p));
    command_p->command_p = strdup(request_p->command_p);
    command_p->bunga.server_p = self_p;
    command_p->bunga.client_p = client_p;
    command_p->queue_p = &queue;
    ml_spawn((ml_worker_pool_job_entry_t)execute_command_job, command_p);
}

static void get_file_add_data(struct client_t *client_p,
                              struct bunga_get_file_rsp_t *response_p,
                              uint8_t *buf_p,
                              size_t size)
{
    response_p->data.buf_p = buf_p;
    response_p->data.size = fread(buf_p, 1, size, client_p->fget_p);

    if (response_p->data.size == 0) {
        if (ferror(client_p->fget_p) != 0) {
            response_p->error_p = "Read error.";
        }

        fclose(client_p->fget_p);
        client_p->fget_p = NULL;
    }
}

static void get_file_fill_window(struct bunga_server_t *self_p,
                                 struct client_t *client_p,
                                 uint8_t *buf_p,
                                 size_t size)
{
    struct bunga_get_file_rsp_t *response_p;

    while (client_p->outstanding_responses < client_p->window_size) {
        response_p = bunga_server_init_get_file_rsp(self_p);
        get_file_add_data(client_p, response_p, buf_p, size);
        bunga_server_reply(self_p);

        if (response_p->data.size == 0) {
            break;
        }

        client_p->outstanding_responses++;
    }
}

static void get_file_open(struct bunga_server_t *self_p,
                          struct client_t *client_p,
                          struct bunga_get_file_req_t *request_p)
{
    struct bunga_get_file_rsp_t *response_p;
    struct stat statbuf;
    uint8_t buf[BUNGA_MESSAGE_SIZE_MAX - 64];

    response_p = bunga_server_init_get_file_rsp(self_p);

    if (client_p->fget_p != NULL) {
        fclose(client_p->fget_p);
    }

    client_p->outstanding_responses = 0;
    client_p->fget_p = fopen(request_p->path_p, "rb");

    if (client_p->fget_p != NULL) {
        if (stat(request_p->path_p, &statbuf) == 0) {
            client_p->window_size = request_p->window_size;

            if (client_p->window_size == 0) {
                client_p->window_size = BUNGA_GET_FILE_WINDOW_SIZE;
            }

            response_p->size = statbuf.st_size;
            get_file_add_data(client_p, response_p, &buf[0], sizeof(buf));
        } else {
            fclose(client_p->fget_p);
            client_p->fget_p = NULL;
            response_p->error_p = strerror(errno);
        }
    } else {
        response_p->error_p = strerror(errno);
    }

    bunga_server_reply(self_p);

    if (response_p->data.size > 0) {
        client_p->outstanding_responses++;
        get_file_fill_window(self_p, client_p, &buf[0], sizeof(buf));
    }
}

static void get_file_data(struct bunga_server_t *self_p,
                          struct client_t *client_p,
                          struct bunga_get_file_req_t *request_p)
{
    uint8_t buf[BUNGA_MESSAGE_SIZE_MAX - 64];

    if (request_p->acknowledge_count > client_p->outstanding_responses) {
        fclose(client_p->fget_p);
        client_p->fget_p = NULL;

        return;
    }

    client_p->outstanding_responses -= request_p->acknowledge_count;

    get_file_fill_window(self_p, client_p, &buf[0], sizeof(buf));
}

static void on_get_file_req(struct bunga_server_t *self_p,
                            struct bunga_server_client_t *bunga_client_p,
                            struct bunga_get_file_req_t *request_p)
{
    struct client_t *client_p;

    client_p = client_from_bunga_client(bunga_client_p);

    if (strlen(request_p->path_p) > 0) {
        get_file_open(self_p, client_p, request_p);
    } else if (client_p->fget_p != NULL) {
        get_file_data(self_p, client_p, request_p);
    }

}

static void put_file_open(struct client_t *client_p,
                          struct bunga_put_file_req_t *request_p,
                          struct bunga_put_file_rsp_t *response_p)
{
    if (client_p->fput_p != NULL) {
        fclose(client_p->fput_p);
    }

    response_p->window_size = BUNGA_PUT_FILE_WINDOW_SIZE;
    client_p->fput_p = fopen(request_p->path_p, "wb");

    if (client_p->fput_p == NULL) {
        response_p->error_p = "Open failed.";
    }
}

static void put_file_data(struct client_t *client_p,
                          struct bunga_put_file_req_t *request_p,
                          struct bunga_put_file_rsp_t *response_p)
{
    size_t items_written;

    if (client_p->fput_p != NULL) {
        items_written = fwrite(request_p->data.buf_p,
                               request_p->data.size,
                               1,
                               client_p->fput_p);

        if (items_written != 1) {
            response_p->error_p = "Write failed.";
            fclose(client_p->fput_p);
            client_p->fput_p = NULL;
        }
    } else {
        response_p->error_p = "No file open.";
    }
}

static void put_file_close(struct client_t *client_p)
{
    fclose(client_p->fput_p);
    client_p->fput_p = NULL;
}

static void on_put_file_req(struct bunga_server_t *self_p,
                            struct bunga_server_client_t *bunga_client_p,
                            struct bunga_put_file_req_t *request_p)
{
    struct client_t *client_p;
    struct bunga_put_file_rsp_t *response_p;

    client_p = client_from_bunga_client(bunga_client_p);
    response_p = bunga_server_init_put_file_rsp(self_p);
    response_p->acknowledge_count = 1;

    if (strlen(request_p->path_p) > 0) {
        put_file_open(client_p, request_p, response_p);
    } else if (request_p->data.size > 0) {
        put_file_data(client_p, request_p, response_p);
    } else if (client_p->fput_p != NULL) {
        put_file_close(client_p);
    }

    bunga_server_reply(self_p);
}

static void handle_execute_command_complete(struct execute_command_t *command_p)
{
    struct bunga_execute_command_rsp_t *response_p;
    char *output_p;
    size_t offset;
    size_t size;
    size_t chunk_size;
    struct bunga_server_t *server_p;
    struct bunga_server_client_t *client_p;

    server_p = command_p->bunga.server_p;
    client_p = command_p->bunga.client_p;

    /* Output. */
    output_p = command_p->output.buf_p;
    size = command_p->output.size;
    chunk_size = 96;

    for (offset = 0; offset < size; offset += chunk_size) {
        if ((size - offset) < 96) {
            chunk_size = (size - offset);
        }

        response_p = bunga_server_init_execute_command_rsp(server_p);
        response_p->output.size = chunk_size;
        response_p->output.buf_p = (uint8_t *)&output_p[offset];
        bunga_server_send(server_p, client_p);
    }

    /* Command result. */
    response_p = bunga_server_init_execute_command_rsp(server_p);

    if (command_p->res != 0) {
        response_p->error_p = strerror(-command_p->res);
    }

    bunga_server_send(server_p, client_p);

    free(command_p->command_p);

    if (command_p->output.buf_p != NULL) {
        free(command_p->output.buf_p);
    }

    ml_message_free(command_p);
}

static void print_kernel_message(char *message_p,
                                 struct bunga_server_t *server_p,
                                 struct bunga_server_client_t *client_p)
{
    unsigned long long secs;
    unsigned long long usecs;
    int text_pos;
    char *text_p;
    char *match_p;
    char header[32];
    struct bunga_log_entry_ind_t *indication_p;

    if (sscanf(message_p, "%*u,%*u,%llu,%*[^;]; %n", &usecs, &text_pos) != 1) {
        return;
    }

    text_p = &message_p[text_pos];
    match_p = strchr(text_p, '\n');

    if (match_p != NULL) {
        *match_p = '\0';
    }

    secs = (usecs / 1000000);
    usecs %= 1000000;

    snprintf(&header[0], sizeof(header), "[%5lld.%06lld] ", secs, usecs);
    indication_p = bunga_server_init_log_entry_ind(server_p);

    if (bunga_log_entry_ind_text_alloc(indication_p, 2) != 0) {
        return;
    }

    indication_p->text.items_pp[0] = &header[0];
    indication_p->text.items_pp[1] = text_p;
    bunga_server_send(server_p, client_p);
}

static struct client_t *find_log_client(int log_fd)
{
    int i;

    for (i = 0; i < 2; i++) {
        if (log_fd == clients[i].log_fd) {
            return (&clients[i]);
        }
    }

    return (NULL);
}

static bool handle_log(struct bunga_server_t *server_p, int log_fd)
{
    char message[512];
    ssize_t size;
    struct client_t *client_p;

    client_p = find_log_client(log_fd);

    if (client_p == NULL) {
        return (false);
    }

    while (true) {
        size = read(log_fd, &message[0], sizeof(message) - 1);

        if (size <= 0) {
            break;
        }

        message[size] = '\0';
        print_kernel_message(&message[0],
                             server_p,
                             client_to_bunga_client(client_p));
    }

    return (true);
}

static void on_put_signal_event(int *fd_p)
{
    uint64_t value;
    ssize_t size;

    value = 1;
    size = write(*fd_p, &value, sizeof(value));
    (void)size;
}

static void *server_main()
{
    struct bunga_server_t server;
    int put_fd;
    struct epoll_event event;
    int res;
    struct ml_uid_t *uid_p;
    void *message_p;
    uint64_t value;
    int i;

    pthread_setname_np(pthread_self(), "bunga_server");

    epoll_fd = epoll_create1(0);

    if (epoll_fd == -1) {
        return (NULL);
    }

    put_fd = eventfd(0, EFD_SEMAPHORE);

    if (put_fd == -1) {
        return (NULL);
    }

    event.events = EPOLLIN;
    event.data.fd = put_fd;

    res = epoll_ctl(epoll_fd, EPOLL_CTL_ADD, put_fd, &event);

    if (res == -1) {
        return (NULL);
    }

    ml_queue_init(&queue, 32);
    ml_queue_set_on_put(&queue, (ml_queue_put_t)on_put_signal_event, &put_fd);

    res = bunga_server_init(&server,
                            "tcp://:28000",
                            &bunga_clients[0],
                            2,
                            &clients_input_buffers[0][0],
                            sizeof(clients_input_buffers[0]),
                            &message[0],
                            sizeof(message),
                            &workspace_in[0],
                            sizeof(workspace_in),
                            &workspace_out[0],
                            sizeof(workspace_out),
                            on_client_connected,
                            on_client_disconnected,
                            on_connect_req,
                            on_execute_command_req,
                            on_get_file_req,
                            on_put_file_req,
                            epoll_fd,
                            NULL);

    if (res != 0) {
        return (NULL);
    }

    for (i = 0; i < 2; i++) {
        client_init(&clients[i]);
    }

    res = bunga_server_start(&server);

    if (res != 0) {
        return (NULL);
    }

    while (true) {
        res = epoll_wait(epoll_fd, &event, 1, -1);

        if (res != 1) {
            break;
        }

        if (event.data.fd == put_fd) {
            res = read(put_fd, &value, sizeof(value));
            (void)res;
            uid_p = ml_queue_get(&queue, &message_p);

            if (uid_p == &uid_execute_command_complete) {
                handle_execute_command_complete(message_p);
            }
        } else if (handle_log(&server, event.data.fd)) {
        } else {
            bunga_server_process(&server, event.data.fd, event.events);
        }
    }

    return (NULL);
}

void bunga_server_linux_create(void)
{
    pthread_t pthread;

    pthread_create(&pthread, NULL, server_main, NULL);
}
