#include <errno.h>
#include <pthread.h>
#include <sys/eventfd.h>
#include <sys/epoll.h>
#include <unistd.h>
#include <fcntl.h>
#include "nala.h"
#include "ml/ml.h"
#include "bunga_server.h"
#include "bunga_server_linux.h"

#define EPOLL_FD                              10
#define PUT_FD                                11
#define CLIENT_FD                             12
#define LOG_FD                                13

static struct bunga_server_t *bunga_server_p;
static struct bunga_server_client_t *bunga_clients_p;
static int pthread_create_handle;
static int bunga_server_init_handle;
static struct bunga_connect_rsp_t connect_rsp;
static struct bunga_execute_command_rsp_t execute_command_rsp[10];

static void call_server_main(void)
{
    pthread_create_mock_get_params_in(pthread_create_handle)->start_routine(NULL);
}

static void call_on_client_connected(struct bunga_server_t *self_p)
{
    bunga_server_init_mock_get_params_in(
        bunga_server_init_handle)->on_client_connected(self_p,
                                                       &bunga_clients_p[0]);
}

static void call_on_connect_req(struct bunga_server_t *self_p,
                                struct bunga_connect_req_t *request_p)
{
    bunga_server_init_mock_get_params_in(
        bunga_server_init_handle)->on_connect_req(self_p,
                                                  &bunga_clients_p[0],
                                                  request_p);
}

static void call_on_execute_command_req(
    struct bunga_server_t *self_p,
    struct bunga_execute_command_req_t *request_p)
{
    bunga_server_init_mock_get_params_in(
        bunga_server_init_handle)->on_execute_command_req(self_p,
                                                          &bunga_clients_p[0],
                                                          request_p);
}

static void on_server_init(
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
    bunga_server_on_connect_req_t on_connect_req,
    bunga_server_on_execute_command_req_t on_execute_command_req,
    bunga_server_on_get_file_req_t on_get_file_req,
    bunga_server_on_put_file_req_t on_put_file_req,
    int epoll_fd,
    messi_epoll_ctl_t epoll_ctl)
{
    (void)server_uri_p;
    (void)clients_max;
    (void)clients_input_bufs_p;
    (void)client_input_size;
    (void)message_buf_p;
    (void)message_size;
    (void)workspace_in_buf_p;
    (void)workspace_in_size;
    (void)workspace_out_buf_p;
    (void)workspace_out_size;
    (void)on_client_connected;
    (void)on_client_disconnected;
    (void)on_connect_req;
    (void)on_execute_command_req;
    (void)on_get_file_req;
    (void)on_put_file_req;
    (void)epoll_fd;
    (void)epoll_ctl;

    bunga_server_p = self_p;
    bunga_clients_p = clients_p;
}

static void mock_prepare_server_main_until_epoll()
{
    bunga_server_init_log_entry_ind_mock_none();
    bunga_server_init_put_file_rsp_mock_none();
    bunga_server_init_get_file_rsp_mock_none();
    bunga_log_entry_ind_text_alloc_mock_none();
    pthread_create_handle = pthread_create_mock_once(0);

    bunga_server_linux_create();

    epoll_create1_mock_once(0, EPOLL_FD);
    eventfd_mock_once(0, EFD_SEMAPHORE, PUT_FD);
    epoll_ctl_mock_once(EPOLL_FD, EPOLL_CTL_ADD, PUT_FD, 0);
    ml_queue_init_mock_once(32);
    ml_queue_set_on_put_mock_once();
    bunga_server_init_handle = bunga_server_init_mock_once(
        "tcp://:28000", 2, 512, 512, 576, 576, EPOLL_FD, 0);
    bunga_server_init_mock_set_callback(on_server_init);
    bunga_server_start_mock_ignore_in_once(0);
}

static void execute_command_process_on_client_connected(
    struct bunga_server_t *self_p,
    int fd,
    uint32_t events)
{
    (void)fd;
    (void)events;

    struct epoll_event event;

    open_mock_once("/dev/kmsg", O_RDONLY | O_NONBLOCK, LOG_FD, "");
    event.events = EPOLLIN;
    event.data.fd = LOG_FD;
    epoll_ctl_mock_once(EPOLL_FD, EPOLL_CTL_ADD, LOG_FD, 0);
    epoll_ctl_mock_set_event_in(&event, sizeof(event));

    call_on_client_connected(self_p);
}

static void execute_command_connect_reply(struct bunga_server_t *self_p)
{
    (void)self_p;

    ASSERT_EQ(connect_rsp.keep_alive_timeout, 2);
    ASSERT_EQ(connect_rsp.maximum_message_size, 512);
}

static void execute_command_process_on_connect_req(
    struct bunga_server_t *self_p,
    int fd,
    uint32_t events)
{
    (void)fd;
    (void)events;

    struct bunga_connect_req_t connect_req;

    bunga_server_init_connect_rsp_mock_once(&connect_rsp);
    bunga_server_reply_mock_once();
    bunga_server_reply_mock_set_callback(execute_command_connect_reply);

    call_on_connect_req(self_p, &connect_req);
}

static void shell_execute_command_date(char *line_p, FILE *fout_p)
{
    (void)line_p;

    fprintf(fout_p, "Today!");
}

static void execute_command_process_on_execute_command_req_date(
    struct bunga_server_t *self_p,
    int fd,
    uint32_t events)
{
    (void)fd;
    (void)events;

    struct bunga_execute_command_req_t execute_command_req;
    uint8_t *message_p;
    int alloc_handle;
    int spawn_handle;
    struct nala_ml_message_alloc_params_t *alloc_params_p;
    struct nala_ml_spawn_params_t *spawn_params_p;

    message_p = nala_alloc(56);
    alloc_handle = ml_message_alloc_mock_once(56, message_p);
    spawn_handle = ml_spawn_mock_once();

    execute_command_req.command_p = "date";
    call_on_execute_command_req(self_p, &execute_command_req);
    alloc_params_p = ml_message_alloc_mock_get_params_in(alloc_handle);

    spawn_params_p = ml_spawn_mock_get_params_in(spawn_handle);
    ml_shell_execute_command_mock_once("date", 0);
    ml_shell_execute_command_mock_set_callback(shell_execute_command_date);
    ml_queue_put_mock_once();

    spawn_params_p->entry(spawn_params_p->arg_p);

    ml_queue_get_mock_once(alloc_params_p->uid_p);
    ml_queue_get_mock_set_message_pp_out((void **)&message_p, sizeof(message_p));
}

static void execute_command_send_output(struct bunga_server_t *self_p,
                                        struct bunga_server_client_t *client_p)
{
    (void)self_p;
    (void)client_p;

    ASSERT_EQ(execute_command_rsp[0].error_p, "");
    ASSERT_EQ(execute_command_rsp[0].output.size, 6);
    ASSERT_MEMORY_EQ(execute_command_rsp[0].output.buf_p, "Today!", 6);
}

static void execute_command_send_result(struct bunga_server_t *self_p,
                                        struct bunga_server_client_t *client_p)
{
    (void)self_p;
    (void)client_p;

    ASSERT_EQ(execute_command_rsp[1].error_p, "");
    ASSERT_EQ(execute_command_rsp[1].output.size, 0);
}

static void mock_prepare_tcp_connect(void)
{
    struct epoll_event event;

    epoll_wait_mock_once(10, 1, -1, 1);
    event.events = EPOLLIN;
    event.data.fd = CLIENT_FD;
    epoll_wait_mock_set_events_out(&event, sizeof(event));
    bunga_server_process_mock_once(CLIENT_FD, event.events);
    bunga_server_process_mock_set_callback(
        execute_command_process_on_client_connected);
}

static void mock_prepare_connect(void)
{
    struct epoll_event event;

    epoll_wait_mock_once(10, 1, -1, 1);
    event.events = EPOLLIN;
    event.data.fd = CLIENT_FD;
    epoll_wait_mock_set_events_out(&event, sizeof(event));
    bunga_server_process_mock_once(CLIENT_FD, event.events);
    bunga_server_process_mock_set_callback(execute_command_process_on_connect_req);
}

static void mock_prepare_execute_command(
    void (*callback)(struct bunga_server_t *self_p,
                     int fd,
                     uint32_t events))
{
    struct epoll_event event;

    epoll_wait_mock_once(10, 1, -1, 1);
    event.events = EPOLLIN;
    event.data.fd = CLIENT_FD;
    epoll_wait_mock_set_events_out(&event, sizeof(event));
    bunga_server_process_mock_once(CLIENT_FD, event.events);
    bunga_server_process_mock_set_callback(callback);
}

TEST(execute_command_date_ok)
{
    struct epoll_event event;

    mock_prepare_server_main_until_epoll();
    mock_prepare_tcp_connect();
    mock_prepare_connect();
    mock_prepare_execute_command(
        execute_command_process_on_execute_command_req_date);

    /* Execute command completion. */
    epoll_wait_mock_once(10, 1, -1, 1);
    event.events = EPOLLIN;
    event.data.fd = PUT_FD;
    epoll_wait_mock_set_events_out(&event, sizeof(event));

    execute_command_rsp[0].error_p = "";
    execute_command_rsp[0].output.size = 0;
    bunga_server_init_execute_command_rsp_mock_once(&execute_command_rsp[0]);
    bunga_server_send_mock_once();
    bunga_server_send_mock_set_callback(execute_command_send_output);

    execute_command_rsp[1].error_p = "";
    execute_command_rsp[1].output.size = 0;
    bunga_server_init_execute_command_rsp_mock_once(&execute_command_rsp[1]);
    bunga_server_send_mock_once();
    bunga_server_send_mock_set_callback(execute_command_send_result);

    ml_message_free_mock_once();

    /* End loop. */
    epoll_wait_mock_once(10, 1, -1, -1);

    call_server_main();
}

static void execute_command_process_on_execute_command_req_date_error(
    struct bunga_server_t *self_p,
    int fd,
    uint32_t events)
{
    (void)fd;
    (void)events;

    struct bunga_execute_command_req_t execute_command_req;
    uint8_t *message_p;
    int alloc_handle;
    int spawn_handle;
    struct nala_ml_message_alloc_params_t *alloc_params_p;
    struct nala_ml_spawn_params_t *spawn_params_p;

    message_p = nala_alloc(56);
    alloc_handle = ml_message_alloc_mock_once(56, message_p);
    spawn_handle = ml_spawn_mock_once();

    execute_command_req.command_p = "date";
    call_on_execute_command_req(self_p, &execute_command_req);
    alloc_params_p = ml_message_alloc_mock_get_params_in(alloc_handle);

    spawn_params_p = ml_spawn_mock_get_params_in(spawn_handle);
    ml_shell_execute_command_mock_once("date", -EINVAL);
    ml_queue_put_mock_once();

    spawn_params_p->entry(spawn_params_p->arg_p);

    ml_queue_get_mock_once(alloc_params_p->uid_p);
    ml_queue_get_mock_set_message_pp_out((void **)&message_p, sizeof(message_p));
}

static void execute_command_send_error(struct bunga_server_t *self_p,
                                       struct bunga_server_client_t *client_p)
{
    (void)self_p;
    (void)client_p;

    ASSERT_EQ(execute_command_rsp[0].error_p, "Invalid argument");
    ASSERT_EQ(execute_command_rsp[0].output.size, 0);
}

TEST(execute_command_date_error)
{
    struct epoll_event event;

    mock_prepare_server_main_until_epoll();
    mock_prepare_tcp_connect();
    mock_prepare_connect();
    mock_prepare_execute_command(
        execute_command_process_on_execute_command_req_date_error);

    /* Execute command completion. */
    epoll_wait_mock_once(10, 1, -1, 1);
    event.events = EPOLLIN;
    event.data.fd = PUT_FD;
    epoll_wait_mock_set_events_out(&event, sizeof(event));

    execute_command_rsp[0].error_p = "";
    execute_command_rsp[0].output.size = 0;
    bunga_server_init_execute_command_rsp_mock_once(&execute_command_rsp[0]);
    bunga_server_send_mock_once();
    bunga_server_send_mock_set_callback(execute_command_send_error);

    ml_message_free_mock_once();

    /* End loop. */
    epoll_wait_mock_once(10, 1, -1, -1);

    call_server_main();
}
