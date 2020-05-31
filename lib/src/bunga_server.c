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
 */

/* This file was generated by Messi. */

#include <errno.h>
#include <unistd.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/epoll.h>
#include <sys/timerfd.h>
#include "messi.h"
#include "bunga_server.h"

static struct bunga_server_client_t *alloc_client(struct bunga_server_t *self_p)
{
    struct bunga_server_client_t *client_p;

    client_p = self_p->clients.free_list_p;

    if (client_p != NULL) {
        /* Remove from free list. */
        self_p->clients.free_list_p = client_p->next_p;

        /* Add to connected list. */
        client_p->next_p = self_p->clients.connected_list_p;

        if (self_p->clients.connected_list_p != NULL) {
            self_p->clients.connected_list_p->prev_p = client_p;
        }

        self_p->clients.connected_list_p = client_p;
    }

    return (client_p);
}

static void remove_client_from_list(struct bunga_server_client_t **list_pp,
                                    struct bunga_server_client_t *client_p)
{
    if (client_p == *list_pp) {
        *list_pp = client_p->next_p;
    } else {
        client_p->prev_p->next_p = client_p->next_p;
    }

    if (client_p->next_p != NULL) {
        client_p->next_p->prev_p = client_p->prev_p;
    }
}

static void free_connected_client(struct bunga_server_t *self_p,
                                  struct bunga_server_client_t *client_p)
{
    remove_client_from_list(&self_p->clients.connected_list_p,
                            client_p);

    /* Add to free list. */
    client_p->next_p = self_p->clients.free_list_p;
    self_p->clients.free_list_p = client_p;
}

static void free_pending_disconnect_client(struct bunga_server_t *self_p,
                                           struct bunga_server_client_t *client_p)
{
    remove_client_from_list(&self_p->clients.pending_disconnect_list_p,
                            client_p);

    /* Add to free list. */
    client_p->next_p = self_p->clients.free_list_p;
    self_p->clients.free_list_p = client_p;
}

static void move_client_to_pending_disconnect_list(
    struct bunga_server_t *self_p,
    struct bunga_server_client_t *client_p)
{
    remove_client_from_list(&self_p->clients.connected_list_p,
                            client_p);

    /* Add to pending disconnect list. */
    client_p->next_p = self_p->clients.pending_disconnect_list_p;
    self_p->clients.pending_disconnect_list_p = client_p;
}

static int epoll_ctl_add(struct bunga_server_t *self_p, int fd)
{
    return (self_p->epoll_ctl(self_p->epoll_fd, EPOLL_CTL_ADD, fd, EPOLLIN));
}

static int epoll_ctl_del(struct bunga_server_t *self_p, int fd)
{
    return (self_p->epoll_ctl(self_p->epoll_fd, EPOLL_CTL_DEL, fd, 0));
}

static int epoll_ctl_mod(struct bunga_server_t *self_p, int fd, uint32_t events)
{
    return (self_p->epoll_ctl(self_p->epoll_fd, EPOLL_CTL_MOD, fd, events));
}

static void close_fd(struct bunga_server_t *self_p, int fd)
{
    epoll_ctl_del(self_p, fd);
    close(fd);
}

static void client_reset_input(struct bunga_server_client_t *self_p)
{
    self_p->input.state = bunga_server_client_input_state_header_t;
    self_p->input.size = 0;
    self_p->input.left = sizeof(struct messi_header_t);
}

static int client_start_keep_alive_timer(struct bunga_server_client_t *self_p)
{
    struct itimerspec timeout;

    memset(&timeout, 0, sizeof(timeout));
    timeout.it_value.tv_sec = 3;

    return (timerfd_settime(self_p->keep_alive_timer_fd, 0, &timeout, NULL));
}

static int client_init(struct bunga_server_client_t *self_p,
                       struct bunga_server_t *server_p,
                       int client_fd)
{
    int res;

    self_p->client_fd = client_fd;
    client_reset_input(self_p);
    self_p->output.head_p = NULL;
    self_p->keep_alive_timer_fd = timerfd_create(CLOCK_MONOTONIC, 0);

    if (self_p->keep_alive_timer_fd == -1) {
        return (-1);
    }

    res = client_start_keep_alive_timer(self_p);

    if (res == -1) {
        goto out1;
    }

    res = epoll_ctl_add(server_p, self_p->keep_alive_timer_fd);

    if (res == -1) {
        goto out1;
    }

    res = epoll_ctl_add(server_p, client_fd);

    if (res == -1) {
        goto out2;
    }

    return (0);

 out2:
    epoll_ctl_del(server_p, self_p->keep_alive_timer_fd);

 out1:
    close(self_p->keep_alive_timer_fd);

    return (-1);
}

static void destroy_pending_disconnect_clients(struct bunga_server_t *self_p)
{
    struct bunga_server_client_t *client_p;
    struct bunga_server_client_t *next_client_p;

    client_p = self_p->clients.pending_disconnect_list_p;

    while (client_p != NULL) {
        close_fd(self_p, client_p->keep_alive_timer_fd);
        client_p->keep_alive_timer_fd = -1;
        self_p->on_client_disconnected(self_p, client_p);
        next_client_p = client_p->next_p;
        free_pending_disconnect_client(self_p, client_p);
        client_p = next_client_p;
    }
}

static void free_client_output(struct bunga_server_client_t *self_p)
{
    struct bunga_server_client_output_item_t *item_p;
    struct bunga_server_client_output_item_t *next_p;

    item_p = self_p->output.head_p;
    self_p->output.head_p = NULL;

    while (item_p != NULL) {
        next_p = item_p->next_p;
        free(item_p);
        item_p = next_p;
    }
}

static void client_pending_disconnect(struct bunga_server_client_t *self_p,
                                      struct bunga_server_t *server_p)
{
    /* Already pending disconnect? */
    if (self_p->client_fd == -1) {
        return;
    }

    close_fd(server_p, self_p->client_fd);
    self_p->client_fd = -1;
    free_client_output(self_p);
    move_client_to_pending_disconnect_list(server_p, self_p);
}

static void process_listener(struct bunga_server_t *self_p, uint32_t events)
{
    (void)events;

    int res;
    int client_fd;
    struct bunga_server_client_t *client_p;

    client_fd = accept(self_p->listener_fd, NULL, 0);

    if (client_fd == -1) {
        return;
    }

    res = messi_make_non_blocking(client_fd);

    if (res == -1) {
        goto out1;
    }

    client_p = alloc_client(self_p);

    if (client_p == NULL) {
        goto out1;
    }

    res = client_init(client_p, self_p, client_fd);

    if (res != 0) {
        goto out2;
    }

    self_p->on_client_connected(self_p, client_p);

    return;

 out2:
    free_connected_client(self_p, client_p);

 out1:
    close(client_fd);
}

static void client_output_append(struct bunga_server_client_t *self_p,
                                 struct bunga_server_t *server_p,
                                 uint8_t *buf_p,
                                 size_t size)
{
    struct bunga_server_client_output_item_t *item_p;

    item_p = malloc(sizeof(*item_p) + size - 1);

    if (item_p == NULL) {
        return;
    }

    item_p->offset = 0;
    item_p->size = size;
    item_p->next_p = NULL;
    memcpy(&item_p->data[0], buf_p, size);

    if (self_p->output.head_p == NULL) {
        self_p->output.head_p = item_p;
        epoll_ctl_mod(server_p, self_p->client_fd, EPOLLIN | EPOLLOUT);
    } else {
        self_p->output.tail_p->next_p = item_p;
    }

    self_p->output.tail_p = item_p;
}

static void client_write(struct bunga_server_t *self_p,
                         struct bunga_server_client_t *client_p,
                         uint8_t *buf_p,
                         size_t size)
{
    size_t offset;
    ssize_t res;

    if (client_p->output.head_p != NULL) {
        client_output_append(client_p, self_p, buf_p, size);

        return;
    }

    offset = 0;

    while (size > 0) {
        res = write(client_p->client_fd, &buf_p[offset], size);

        if (res == (ssize_t)size) {
            break;
        } else if (res > 0) {
            offset += res;
            size -= res;
        } else if ((res == -1) && (errno == EAGAIN)) {
            client_output_append(client_p, self_p, &buf_p[offset], size);
            break;
        } else {
            client_pending_disconnect(client_p, self_p);
            break;
        }
    }
}

static int handle_message_user(struct bunga_server_t *self_p,
                               struct bunga_server_client_t *client_p)
{
    int res;
    struct bunga_client_to_server_t *message_p;
    uint8_t *payload_buf_p;
    size_t payload_size;

    self_p->input.message_p = bunga_client_to_server_new(
        &self_p->input.workspace.buf_p[0],
        self_p->input.workspace.size);
    message_p = self_p->input.message_p;

    if (message_p == NULL) {
        return (-1);
    }

    payload_buf_p = &client_p->input.data.buf_p[sizeof(struct messi_header_t)];
    payload_size = client_p->input.size - sizeof(struct messi_header_t);

    res = bunga_client_to_server_decode(message_p, payload_buf_p, payload_size);

    if (res != (int)payload_size) {
        return (-1);
    }

    self_p->current_client_p = client_p;

    switch (message_p->messages.choice) {

    case bunga_client_to_server_messages_choice_execute_command_req_e:
        self_p->on_execute_command_req(
            self_p,
            client_p,
            &message_p->messages.value.execute_command_req);
        break;

    default:
        break;
    }

    self_p->current_client_p = NULL;

    return (0);
}

static int handle_message_ping(struct bunga_server_t *self_p,
                               struct bunga_server_client_t *client_p)
{
    int res;
    struct messi_header_t header;

    res = client_start_keep_alive_timer(client_p);

    if (res != 0) {
        return (res);
    }

    header.type = MESSI_MESSAGE_TYPE_PONG;
    messi_header_set_size(&header, 0);
    client_write(self_p, client_p, (uint8_t *)&header, sizeof(header));

    return (0);
}

static int handle_message(struct bunga_server_t *self_p,
                          struct bunga_server_client_t *client_p,
                          uint32_t type)
{
    int res;

    switch (type) {

    case MESSI_MESSAGE_TYPE_CLIENT_TO_SERVER_USER:
        res = handle_message_user(self_p, client_p);
        break;

    case MESSI_MESSAGE_TYPE_PING:
        res = handle_message_ping(self_p, client_p);
        break;

    default:
        res = -1;
        break;
    }

    return (res);
}

static void process_client_socket_out(struct bunga_server_t *self_p,
                                      struct bunga_server_client_t *client_p)
{
    struct bunga_server_client_output_item_t *item_p;
    struct bunga_server_client_output_item_t *next_p;
    ssize_t res;

    item_p = client_p->output.head_p;

    while (item_p != NULL) {
        res = write(client_p->client_fd,
                    &item_p->data[item_p->offset],
                    item_p->size);

        if (res == (ssize_t)item_p->size) {
            next_p = item_p->next_p;
            free(item_p);
            item_p = next_p;
        } else if (res > 0) {
            item_p->offset += res;
            item_p->size -= res;
        } else if ((res == -1) && (errno == EAGAIN)) {
            break;
        } else {
            client_pending_disconnect(client_p, self_p);
            break;
        }
    }

    client_p->output.head_p = item_p;

    if (item_p == NULL) {
        epoll_ctl_mod(self_p, client_p->client_fd, EPOLLIN);
    }
}

static void process_client_socket_in(struct bunga_server_t *self_p,
                                     struct bunga_server_client_t *client_p)
{
    int res;
    ssize_t size;
    struct messi_header_t *header_p;

    header_p = (struct messi_header_t *)client_p->input.data.buf_p;

    while (true) {
        size = read(client_p->client_fd,
                    &client_p->input.data.buf_p[client_p->input.size],
                    client_p->input.left);

        if (size <= 0) {
            if (!((size == -1) && (errno == EAGAIN))) {
                client_pending_disconnect(client_p, self_p);
            }

            break;
        }

        client_p->input.size += size;
        client_p->input.left -= size;

        if (client_p->input.left > 0) {
            continue;
        }

        if (client_p->input.state == bunga_server_client_input_state_header_t) {
            client_p->input.left = messi_header_get_size(header_p);

            if ((client_p->input.left + sizeof(*header_p))
                > client_p->input.data.size) {
                client_pending_disconnect(client_p, self_p);
                break;
            }

            client_p->input.state = bunga_server_client_input_state_payload_t;
        }

        if (client_p->input.left == 0) {
            res = handle_message(self_p, client_p, header_p->type);

            if (res == 0) {
                client_reset_input(client_p);
            } else {
                client_pending_disconnect(client_p, self_p);
                break;
            }
        }
    }
}

static void process_client_socket(struct bunga_server_t *self_p,
                                  struct bunga_server_client_t *client_p,
                                  uint32_t events)
{
    if (events & EPOLLOUT) {
        process_client_socket_out(self_p, client_p);
    }

    if (events & EPOLLIN) {
        process_client_socket_in(self_p, client_p);
    }
}

static void process_client_keep_alive_timer(struct bunga_server_t *self_p,
                                            struct bunga_server_client_t *client_p)
{
    client_pending_disconnect(client_p, self_p);
}

static void on_execute_command_req_default(
    struct bunga_server_t *self_p,
    struct bunga_server_client_t *client_p,
    struct bunga_execute_command_req_t *message_p)
{
    (void)self_p;
    (void)client_p;
    (void)message_p;
}

static int encode_user_message(struct bunga_server_t *self_p)
{
    int payload_size;
    struct messi_header_t *header_p;

    payload_size = bunga_server_to_client_encode(
        self_p->output.message_p,
        &self_p->output.encoded.buf_p[sizeof(*header_p)],
        self_p->output.encoded.size - sizeof(*header_p));

    if (payload_size < 0) {
        return (payload_size);
    }

    header_p = (struct messi_header_t *)self_p->output.encoded.buf_p;
    header_p->type = MESSI_MESSAGE_TYPE_SERVER_TO_CLIENT_USER;
    messi_header_set_size(header_p, payload_size);

    return (payload_size + sizeof(*header_p));
}

static void on_client_connected_default(struct bunga_server_t *self_p,
                                        struct bunga_server_client_t *client_p)
{
        (void)self_p;
        (void)client_p;
}

static void on_client_disconnected_default(struct bunga_server_t *self_p,
                                           struct bunga_server_client_t *client_p)
{
        (void)self_p;
        (void)client_p;
}

void bunga_server_new_output_message(struct bunga_server_t *self_p)
{
    self_p->output.message_p = bunga_server_to_client_new(
        &self_p->output.workspace.buf_p[0],
        self_p->output.workspace.size);
}

int bunga_server_init(
    struct bunga_server_t *self_p,
    const char *server_uri_p,
    struct bunga_server_client_t *clients_p,
    int clients_max,
    uint8_t *clients_input_bufs_p,
    size_t client_input_size,
    uint8_t *message_buf_p,
    size_t message_size,
    uint8_t *workspace_in_buf_p,
    size_t workspace_in_size,
    uint8_t *workspace_out_buf_p,
    size_t workspace_out_size,
    bunga_server_on_client_connected_t on_client_connected,
    bunga_server_on_client_disconnected_t on_client_disconnected,
    bunga_server_on_execute_command_req_t on_execute_command_req,
    int epoll_fd,
    messi_epoll_ctl_t epoll_ctl)
{
    (void)clients_max;

    int i;
    int res;

    if (on_execute_command_req == NULL) {
        on_execute_command_req = on_execute_command_req_default;
    }

    if (on_client_connected == NULL) {
        on_client_connected = on_client_connected_default;
    }

    if (on_client_disconnected == NULL) {
        on_client_disconnected = on_client_disconnected_default;
    }

    if (epoll_ctl == NULL) {
        epoll_ctl = messi_epoll_ctl_default;
    }

    res = messi_parse_tcp_uri(server_uri_p,
                              &self_p->server.address[0],
                              sizeof(self_p->server.address),
                              &self_p->server.port);

    if (res != 0) {
        return (res);
    }

    self_p->on_execute_command_req = on_execute_command_req;
    self_p->epoll_fd = epoll_fd;
    self_p->epoll_ctl = epoll_ctl;

    /* Lists of clients. */
    self_p->clients.free_list_p = &clients_p[0];
    self_p->clients.input_buffer_size = client_input_size;

    for (i = 0; i < clients_max - 1; i++) {
        clients_p[i].next_p = &clients_p[i + 1];
        clients_p[i].input.data.buf_p = &clients_input_bufs_p[i * client_input_size];
        clients_p[i].input.data.size = client_input_size;
    }

    clients_p[i].next_p = NULL;
    clients_p[i].input.data.buf_p = &clients_input_bufs_p[i * client_input_size];
    clients_p[i].input.data.size = client_input_size;
    self_p->clients.connected_list_p = NULL;
    self_p->clients.pending_disconnect_list_p = NULL;

    self_p->input.workspace.buf_p = workspace_in_buf_p;
    self_p->input.workspace.size = workspace_in_size;
    self_p->output.encoded.buf_p = message_buf_p;
    self_p->output.encoded.size = message_size;
    self_p->output.workspace.buf_p = workspace_out_buf_p;
    self_p->output.workspace.size = workspace_out_size;
    self_p->on_client_connected = on_client_connected;
    self_p->on_client_disconnected = on_client_disconnected;
    self_p->current_client_p = NULL;

    return (0);
}

int bunga_server_start(struct bunga_server_t *self_p)
{
    int res;
    int listener_fd;
    struct sockaddr_in addr;
    int enable;

    listener_fd = socket(AF_INET, SOCK_STREAM, 0);

    if (listener_fd == -1) {
        return (1);
    }

    enable = 1;

    res = setsockopt(listener_fd,
                     SOL_SOCKET,
                     SO_REUSEADDR,
                     &enable,
                     sizeof(enable));

    if (res != 0) {
        goto out;
    }

    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_port = htons((short)self_p->server.port);

    if (strlen(&self_p->server.address[0]) > 0) {
        res = inet_aton(&self_p->server.address[0],
                        (struct in_addr *)&addr.sin_addr.s_addr);

        if (res != 1) {
            goto out;
        }
    } else {
        addr.sin_addr.s_addr = htonl(INADDR_ANY);
    }

    res = bind(listener_fd, (struct sockaddr *)&addr, sizeof(addr));

    if (res == -1) {
        goto out;
    }

    res = listen(listener_fd, 5);

    if (res == -1) {
        goto out;
    }

    res = messi_make_non_blocking(listener_fd);

    if (res == -1) {
        goto out;
    }

    res = epoll_ctl_add(self_p, listener_fd);

    if (res == -1) {
        goto out;
    }

    self_p->listener_fd = listener_fd;

    return (0);

 out:
    close(listener_fd);

    return (-1);
}

void bunga_server_stop(struct bunga_server_t *self_p)
{
    struct bunga_server_client_t *client_p;
    struct bunga_server_client_t *next_client_p;

    close_fd(self_p, self_p->listener_fd);
    client_p = self_p->clients.connected_list_p;

    while (client_p != NULL) {
        close_fd(self_p, client_p->client_fd);
        close_fd(self_p, client_p->keep_alive_timer_fd);
        free_client_output(client_p);
        next_client_p = client_p->next_p;
        client_p->next_p = self_p->clients.free_list_p;
        self_p->clients.free_list_p = client_p;
        client_p = next_client_p;
    }
}

void bunga_server_process(struct bunga_server_t *self_p, int fd, uint32_t events)
{
    struct bunga_server_client_t *client_p;

    if (fd == self_p->listener_fd) {
        process_listener(self_p, events);
    } else {
        client_p = self_p->clients.connected_list_p;

        while (client_p != NULL) {
            if (fd == client_p->client_fd) {
                process_client_socket(self_p, client_p, events);
                break;
            } else if (fd == client_p->keep_alive_timer_fd) {
                process_client_keep_alive_timer(self_p, client_p);
                break;
            }

            client_p = client_p->next_p;
        }
    }

    destroy_pending_disconnect_clients(self_p);
}

void bunga_server_send(
    struct bunga_server_t *self_p,
    struct bunga_server_client_t *client_p)
{
    int res;

    res = encode_user_message(self_p);

    if (res < 0) {
        return;
    }

    client_write(self_p, client_p, self_p->output.encoded.buf_p, res);
}

void bunga_server_reply(struct bunga_server_t *self_p)
{
    if (self_p->current_client_p != NULL) {
        bunga_server_send(self_p, self_p->current_client_p);
    }
}

void bunga_server_broadcast(struct bunga_server_t *self_p)
{
    int res;
    struct bunga_server_client_t *client_p;
    struct bunga_server_client_t *next_client_p;

    /* Create the message. */
    res = encode_user_message(self_p);

    if (res < 0) {
        return;
    }

    /* Send it to all clients. */
    client_p = self_p->clients.connected_list_p;

    while (client_p != NULL) {
        next_client_p = client_p->next_p;
        client_write(self_p, client_p, self_p->output.encoded.buf_p, res);
        client_p = next_client_p;
    }
}

void bunga_server_disconnect(
    struct bunga_server_t *self_p,
    struct bunga_server_client_t *client_p)
{
    if (client_p == NULL) {
        client_p = self_p->current_client_p;
    }

    if (client_p == NULL) {
        return;
    }

    client_pending_disconnect(client_p, self_p);
}

struct bunga_execute_command_rsp_t *bunga_server_init_execute_command_rsp(
    struct bunga_server_t *self_p)
{
    bunga_server_new_output_message(self_p);
    bunga_server_to_client_messages_execute_command_rsp_init(self_p->output.message_p);

    return (&self_p->output.message_p->messages.value.execute_command_rsp);
}

