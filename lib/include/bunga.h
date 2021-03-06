/**
 * The MIT License (MIT)
 *
 * Copyright (c) 2019 Erik Moqvist
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

/**
 * This file was generated by pbtools.
 */

#ifndef BUNGA_H
#define BUNGA_H

#ifdef __cplusplus
extern "C" {
#endif

#include "pbtools.h"

/**
 * Message bunga.ConnectReq.
 */
struct bunga_connect_req_repeated_t {
    int length;
    struct bunga_connect_req_t *items_p;
};

struct bunga_connect_req_t {
    struct pbtools_message_base_t base;
    uint32_t keep_alive_timeout;
    uint32_t maximum_message_size;
};

/**
 * Message bunga.ExecuteCommandReq.
 */
struct bunga_execute_command_req_repeated_t {
    int length;
    struct bunga_execute_command_req_t *items_p;
};

struct bunga_execute_command_req_t {
    struct pbtools_message_base_t base;
    char *command_p;
};

/**
 * Message bunga.GetFileReq.
 */
struct bunga_get_file_req_repeated_t {
    int length;
    struct bunga_get_file_req_t *items_p;
};

struct bunga_get_file_req_t {
    struct pbtools_message_base_t base;
    char *path_p;
    uint32_t window_size;
    uint32_t acknowledge_count;
};

/**
 * Message bunga.PutFileReq.
 */
struct bunga_put_file_req_repeated_t {
    int length;
    struct bunga_put_file_req_t *items_p;
};

struct bunga_put_file_req_t {
    struct pbtools_message_base_t base;
    char *path_p;
    uint64_t size;
    struct pbtools_bytes_t data;
};

/**
 * Enum bunga.ClientToServer.messages.
 */
enum bunga_client_to_server_messages_choice_e {
    bunga_client_to_server_messages_choice_none_e = 0,
    bunga_client_to_server_messages_choice_connect_req_e = 1,
    bunga_client_to_server_messages_choice_execute_command_req_e = 2,
    bunga_client_to_server_messages_choice_get_file_req_e = 3,
    bunga_client_to_server_messages_choice_put_file_req_e = 4
};

/**
 * Oneof bunga.ClientToServer.messages.
 */
struct bunga_client_to_server_messages_oneof_t {
    enum bunga_client_to_server_messages_choice_e choice;
    union {
        struct bunga_connect_req_t connect_req;
        struct bunga_execute_command_req_t execute_command_req;
        struct bunga_get_file_req_t get_file_req;
        struct bunga_put_file_req_t put_file_req;
    } value;
};

/**
 * Message bunga.ClientToServer.
 */
struct bunga_client_to_server_repeated_t {
    int length;
    struct bunga_client_to_server_t *items_p;
};

struct bunga_client_to_server_t {
    struct pbtools_message_base_t base;
    struct bunga_client_to_server_messages_oneof_t messages;
};

/**
 * Message bunga.ConnectRsp.
 */
struct bunga_connect_rsp_repeated_t {
    int length;
    struct bunga_connect_rsp_t *items_p;
};

struct bunga_connect_rsp_t {
    struct pbtools_message_base_t base;
    uint32_t keep_alive_timeout;
    uint32_t maximum_message_size;
};

/**
 * Message bunga.ExecuteCommandRsp.
 */
struct bunga_execute_command_rsp_repeated_t {
    int length;
    struct bunga_execute_command_rsp_t *items_p;
};

struct bunga_execute_command_rsp_t {
    struct pbtools_message_base_t base;
    struct pbtools_bytes_t output;
    char *error_p;
};

/**
 * Message bunga.LogEntryInd.
 */
struct bunga_log_entry_ind_repeated_t {
    int length;
    struct bunga_log_entry_ind_t *items_p;
};

struct bunga_log_entry_ind_t {
    struct pbtools_message_base_t base;
    struct pbtools_repeated_string_t text;
};

/**
 * Message bunga.GetFileRsp.
 */
struct bunga_get_file_rsp_repeated_t {
    int length;
    struct bunga_get_file_rsp_t *items_p;
};

struct bunga_get_file_rsp_t {
    struct pbtools_message_base_t base;
    uint64_t size;
    struct pbtools_bytes_t data;
    char *error_p;
};

/**
 * Message bunga.PutFileRsp.
 */
struct bunga_put_file_rsp_repeated_t {
    int length;
    struct bunga_put_file_rsp_t *items_p;
};

struct bunga_put_file_rsp_t {
    struct pbtools_message_base_t base;
    uint32_t window_size;
    char *error_p;
    uint32_t acknowledge_count;
};

/**
 * Enum bunga.ServerToClient.messages.
 */
enum bunga_server_to_client_messages_choice_e {
    bunga_server_to_client_messages_choice_none_e = 0,
    bunga_server_to_client_messages_choice_connect_rsp_e = 1,
    bunga_server_to_client_messages_choice_execute_command_rsp_e = 2,
    bunga_server_to_client_messages_choice_log_entry_ind_e = 3,
    bunga_server_to_client_messages_choice_get_file_rsp_e = 4,
    bunga_server_to_client_messages_choice_put_file_rsp_e = 5
};

/**
 * Oneof bunga.ServerToClient.messages.
 */
struct bunga_server_to_client_messages_oneof_t {
    enum bunga_server_to_client_messages_choice_e choice;
    union {
        struct bunga_connect_rsp_t connect_rsp;
        struct bunga_execute_command_rsp_t execute_command_rsp;
        struct bunga_log_entry_ind_t log_entry_ind;
        struct bunga_get_file_rsp_t get_file_rsp;
        struct bunga_put_file_rsp_t put_file_rsp;
    } value;
};

/**
 * Message bunga.ServerToClient.
 */
struct bunga_server_to_client_repeated_t {
    int length;
    struct bunga_server_to_client_t *items_p;
};

struct bunga_server_to_client_t {
    struct pbtools_message_base_t base;
    struct bunga_server_to_client_messages_oneof_t messages;
};

/**
 * Encoding and decoding of bunga.ConnectReq.
 */
struct bunga_connect_req_t *
bunga_connect_req_new(
    void *workspace_p,
    size_t size);

int bunga_connect_req_encode(
    struct bunga_connect_req_t *self_p,
    uint8_t *encoded_p,
    size_t size);

int bunga_connect_req_decode(
    struct bunga_connect_req_t *self_p,
    const uint8_t *encoded_p,
    size_t size);

/**
 * Encoding and decoding of bunga.ExecuteCommandReq.
 */
struct bunga_execute_command_req_t *
bunga_execute_command_req_new(
    void *workspace_p,
    size_t size);

int bunga_execute_command_req_encode(
    struct bunga_execute_command_req_t *self_p,
    uint8_t *encoded_p,
    size_t size);

int bunga_execute_command_req_decode(
    struct bunga_execute_command_req_t *self_p,
    const uint8_t *encoded_p,
    size_t size);

/**
 * Encoding and decoding of bunga.GetFileReq.
 */
struct bunga_get_file_req_t *
bunga_get_file_req_new(
    void *workspace_p,
    size_t size);

int bunga_get_file_req_encode(
    struct bunga_get_file_req_t *self_p,
    uint8_t *encoded_p,
    size_t size);

int bunga_get_file_req_decode(
    struct bunga_get_file_req_t *self_p,
    const uint8_t *encoded_p,
    size_t size);

/**
 * Encoding and decoding of bunga.PutFileReq.
 */
struct bunga_put_file_req_t *
bunga_put_file_req_new(
    void *workspace_p,
    size_t size);

int bunga_put_file_req_encode(
    struct bunga_put_file_req_t *self_p,
    uint8_t *encoded_p,
    size_t size);

int bunga_put_file_req_decode(
    struct bunga_put_file_req_t *self_p,
    const uint8_t *encoded_p,
    size_t size);

void bunga_client_to_server_messages_connect_req_init(
    struct bunga_client_to_server_t *self_p);

void bunga_client_to_server_messages_execute_command_req_init(
    struct bunga_client_to_server_t *self_p);

void bunga_client_to_server_messages_get_file_req_init(
    struct bunga_client_to_server_t *self_p);

void bunga_client_to_server_messages_put_file_req_init(
    struct bunga_client_to_server_t *self_p);

/**
 * Encoding and decoding of bunga.ClientToServer.
 */
struct bunga_client_to_server_t *
bunga_client_to_server_new(
    void *workspace_p,
    size_t size);

int bunga_client_to_server_encode(
    struct bunga_client_to_server_t *self_p,
    uint8_t *encoded_p,
    size_t size);

int bunga_client_to_server_decode(
    struct bunga_client_to_server_t *self_p,
    const uint8_t *encoded_p,
    size_t size);

/**
 * Encoding and decoding of bunga.ConnectRsp.
 */
struct bunga_connect_rsp_t *
bunga_connect_rsp_new(
    void *workspace_p,
    size_t size);

int bunga_connect_rsp_encode(
    struct bunga_connect_rsp_t *self_p,
    uint8_t *encoded_p,
    size_t size);

int bunga_connect_rsp_decode(
    struct bunga_connect_rsp_t *self_p,
    const uint8_t *encoded_p,
    size_t size);

/**
 * Encoding and decoding of bunga.ExecuteCommandRsp.
 */
struct bunga_execute_command_rsp_t *
bunga_execute_command_rsp_new(
    void *workspace_p,
    size_t size);

int bunga_execute_command_rsp_encode(
    struct bunga_execute_command_rsp_t *self_p,
    uint8_t *encoded_p,
    size_t size);

int bunga_execute_command_rsp_decode(
    struct bunga_execute_command_rsp_t *self_p,
    const uint8_t *encoded_p,
    size_t size);

int bunga_log_entry_ind_text_alloc(
    struct bunga_log_entry_ind_t *self_p,
    int length);

/**
 * Encoding and decoding of bunga.LogEntryInd.
 */
struct bunga_log_entry_ind_t *
bunga_log_entry_ind_new(
    void *workspace_p,
    size_t size);

int bunga_log_entry_ind_encode(
    struct bunga_log_entry_ind_t *self_p,
    uint8_t *encoded_p,
    size_t size);

int bunga_log_entry_ind_decode(
    struct bunga_log_entry_ind_t *self_p,
    const uint8_t *encoded_p,
    size_t size);

/**
 * Encoding and decoding of bunga.GetFileRsp.
 */
struct bunga_get_file_rsp_t *
bunga_get_file_rsp_new(
    void *workspace_p,
    size_t size);

int bunga_get_file_rsp_encode(
    struct bunga_get_file_rsp_t *self_p,
    uint8_t *encoded_p,
    size_t size);

int bunga_get_file_rsp_decode(
    struct bunga_get_file_rsp_t *self_p,
    const uint8_t *encoded_p,
    size_t size);

/**
 * Encoding and decoding of bunga.PutFileRsp.
 */
struct bunga_put_file_rsp_t *
bunga_put_file_rsp_new(
    void *workspace_p,
    size_t size);

int bunga_put_file_rsp_encode(
    struct bunga_put_file_rsp_t *self_p,
    uint8_t *encoded_p,
    size_t size);

int bunga_put_file_rsp_decode(
    struct bunga_put_file_rsp_t *self_p,
    const uint8_t *encoded_p,
    size_t size);

void bunga_server_to_client_messages_connect_rsp_init(
    struct bunga_server_to_client_t *self_p);

void bunga_server_to_client_messages_execute_command_rsp_init(
    struct bunga_server_to_client_t *self_p);

void bunga_server_to_client_messages_log_entry_ind_init(
    struct bunga_server_to_client_t *self_p);

void bunga_server_to_client_messages_get_file_rsp_init(
    struct bunga_server_to_client_t *self_p);

void bunga_server_to_client_messages_put_file_rsp_init(
    struct bunga_server_to_client_t *self_p);

/**
 * Encoding and decoding of bunga.ServerToClient.
 */
struct bunga_server_to_client_t *
bunga_server_to_client_new(
    void *workspace_p,
    size_t size);

int bunga_server_to_client_encode(
    struct bunga_server_to_client_t *self_p,
    uint8_t *encoded_p,
    size_t size);

int bunga_server_to_client_decode(
    struct bunga_server_to_client_t *self_p,
    const uint8_t *encoded_p,
    size_t size);

/* Internal functions. Do not use! */

void bunga_connect_req_init(
    struct bunga_connect_req_t *self_p,
    struct pbtools_heap_t *heap_p);

void bunga_connect_req_encode_inner(
    struct pbtools_encoder_t *encoder_p,
    struct bunga_connect_req_t *self_p);

void bunga_connect_req_decode_inner(
    struct pbtools_decoder_t *decoder_p,
    struct bunga_connect_req_t *self_p);

void bunga_connect_req_encode_repeated_inner(
    struct pbtools_encoder_t *encoder_p,
    int field_number,
    struct bunga_connect_req_repeated_t *repeated_p);

void bunga_connect_req_decode_repeated_inner(
    struct pbtools_decoder_t *decoder_p,
    struct pbtools_repeated_info_t *repeated_info_p,
    struct bunga_connect_req_repeated_t *repeated_p);

void bunga_execute_command_req_init(
    struct bunga_execute_command_req_t *self_p,
    struct pbtools_heap_t *heap_p);

void bunga_execute_command_req_encode_inner(
    struct pbtools_encoder_t *encoder_p,
    struct bunga_execute_command_req_t *self_p);

void bunga_execute_command_req_decode_inner(
    struct pbtools_decoder_t *decoder_p,
    struct bunga_execute_command_req_t *self_p);

void bunga_execute_command_req_encode_repeated_inner(
    struct pbtools_encoder_t *encoder_p,
    int field_number,
    struct bunga_execute_command_req_repeated_t *repeated_p);

void bunga_execute_command_req_decode_repeated_inner(
    struct pbtools_decoder_t *decoder_p,
    struct pbtools_repeated_info_t *repeated_info_p,
    struct bunga_execute_command_req_repeated_t *repeated_p);

void bunga_get_file_req_init(
    struct bunga_get_file_req_t *self_p,
    struct pbtools_heap_t *heap_p);

void bunga_get_file_req_encode_inner(
    struct pbtools_encoder_t *encoder_p,
    struct bunga_get_file_req_t *self_p);

void bunga_get_file_req_decode_inner(
    struct pbtools_decoder_t *decoder_p,
    struct bunga_get_file_req_t *self_p);

void bunga_get_file_req_encode_repeated_inner(
    struct pbtools_encoder_t *encoder_p,
    int field_number,
    struct bunga_get_file_req_repeated_t *repeated_p);

void bunga_get_file_req_decode_repeated_inner(
    struct pbtools_decoder_t *decoder_p,
    struct pbtools_repeated_info_t *repeated_info_p,
    struct bunga_get_file_req_repeated_t *repeated_p);

void bunga_put_file_req_init(
    struct bunga_put_file_req_t *self_p,
    struct pbtools_heap_t *heap_p);

void bunga_put_file_req_encode_inner(
    struct pbtools_encoder_t *encoder_p,
    struct bunga_put_file_req_t *self_p);

void bunga_put_file_req_decode_inner(
    struct pbtools_decoder_t *decoder_p,
    struct bunga_put_file_req_t *self_p);

void bunga_put_file_req_encode_repeated_inner(
    struct pbtools_encoder_t *encoder_p,
    int field_number,
    struct bunga_put_file_req_repeated_t *repeated_p);

void bunga_put_file_req_decode_repeated_inner(
    struct pbtools_decoder_t *decoder_p,
    struct pbtools_repeated_info_t *repeated_info_p,
    struct bunga_put_file_req_repeated_t *repeated_p);

void bunga_client_to_server_init(
    struct bunga_client_to_server_t *self_p,
    struct pbtools_heap_t *heap_p);

void bunga_client_to_server_encode_inner(
    struct pbtools_encoder_t *encoder_p,
    struct bunga_client_to_server_t *self_p);

void bunga_client_to_server_decode_inner(
    struct pbtools_decoder_t *decoder_p,
    struct bunga_client_to_server_t *self_p);

void bunga_client_to_server_encode_repeated_inner(
    struct pbtools_encoder_t *encoder_p,
    int field_number,
    struct bunga_client_to_server_repeated_t *repeated_p);

void bunga_client_to_server_decode_repeated_inner(
    struct pbtools_decoder_t *decoder_p,
    struct pbtools_repeated_info_t *repeated_info_p,
    struct bunga_client_to_server_repeated_t *repeated_p);

void bunga_connect_rsp_init(
    struct bunga_connect_rsp_t *self_p,
    struct pbtools_heap_t *heap_p);

void bunga_connect_rsp_encode_inner(
    struct pbtools_encoder_t *encoder_p,
    struct bunga_connect_rsp_t *self_p);

void bunga_connect_rsp_decode_inner(
    struct pbtools_decoder_t *decoder_p,
    struct bunga_connect_rsp_t *self_p);

void bunga_connect_rsp_encode_repeated_inner(
    struct pbtools_encoder_t *encoder_p,
    int field_number,
    struct bunga_connect_rsp_repeated_t *repeated_p);

void bunga_connect_rsp_decode_repeated_inner(
    struct pbtools_decoder_t *decoder_p,
    struct pbtools_repeated_info_t *repeated_info_p,
    struct bunga_connect_rsp_repeated_t *repeated_p);

void bunga_execute_command_rsp_init(
    struct bunga_execute_command_rsp_t *self_p,
    struct pbtools_heap_t *heap_p);

void bunga_execute_command_rsp_encode_inner(
    struct pbtools_encoder_t *encoder_p,
    struct bunga_execute_command_rsp_t *self_p);

void bunga_execute_command_rsp_decode_inner(
    struct pbtools_decoder_t *decoder_p,
    struct bunga_execute_command_rsp_t *self_p);

void bunga_execute_command_rsp_encode_repeated_inner(
    struct pbtools_encoder_t *encoder_p,
    int field_number,
    struct bunga_execute_command_rsp_repeated_t *repeated_p);

void bunga_execute_command_rsp_decode_repeated_inner(
    struct pbtools_decoder_t *decoder_p,
    struct pbtools_repeated_info_t *repeated_info_p,
    struct bunga_execute_command_rsp_repeated_t *repeated_p);

void bunga_log_entry_ind_init(
    struct bunga_log_entry_ind_t *self_p,
    struct pbtools_heap_t *heap_p);

void bunga_log_entry_ind_encode_inner(
    struct pbtools_encoder_t *encoder_p,
    struct bunga_log_entry_ind_t *self_p);

void bunga_log_entry_ind_decode_inner(
    struct pbtools_decoder_t *decoder_p,
    struct bunga_log_entry_ind_t *self_p);

void bunga_log_entry_ind_encode_repeated_inner(
    struct pbtools_encoder_t *encoder_p,
    int field_number,
    struct bunga_log_entry_ind_repeated_t *repeated_p);

void bunga_log_entry_ind_decode_repeated_inner(
    struct pbtools_decoder_t *decoder_p,
    struct pbtools_repeated_info_t *repeated_info_p,
    struct bunga_log_entry_ind_repeated_t *repeated_p);

void bunga_get_file_rsp_init(
    struct bunga_get_file_rsp_t *self_p,
    struct pbtools_heap_t *heap_p);

void bunga_get_file_rsp_encode_inner(
    struct pbtools_encoder_t *encoder_p,
    struct bunga_get_file_rsp_t *self_p);

void bunga_get_file_rsp_decode_inner(
    struct pbtools_decoder_t *decoder_p,
    struct bunga_get_file_rsp_t *self_p);

void bunga_get_file_rsp_encode_repeated_inner(
    struct pbtools_encoder_t *encoder_p,
    int field_number,
    struct bunga_get_file_rsp_repeated_t *repeated_p);

void bunga_get_file_rsp_decode_repeated_inner(
    struct pbtools_decoder_t *decoder_p,
    struct pbtools_repeated_info_t *repeated_info_p,
    struct bunga_get_file_rsp_repeated_t *repeated_p);

void bunga_put_file_rsp_init(
    struct bunga_put_file_rsp_t *self_p,
    struct pbtools_heap_t *heap_p);

void bunga_put_file_rsp_encode_inner(
    struct pbtools_encoder_t *encoder_p,
    struct bunga_put_file_rsp_t *self_p);

void bunga_put_file_rsp_decode_inner(
    struct pbtools_decoder_t *decoder_p,
    struct bunga_put_file_rsp_t *self_p);

void bunga_put_file_rsp_encode_repeated_inner(
    struct pbtools_encoder_t *encoder_p,
    int field_number,
    struct bunga_put_file_rsp_repeated_t *repeated_p);

void bunga_put_file_rsp_decode_repeated_inner(
    struct pbtools_decoder_t *decoder_p,
    struct pbtools_repeated_info_t *repeated_info_p,
    struct bunga_put_file_rsp_repeated_t *repeated_p);

void bunga_server_to_client_init(
    struct bunga_server_to_client_t *self_p,
    struct pbtools_heap_t *heap_p);

void bunga_server_to_client_encode_inner(
    struct pbtools_encoder_t *encoder_p,
    struct bunga_server_to_client_t *self_p);

void bunga_server_to_client_decode_inner(
    struct pbtools_decoder_t *decoder_p,
    struct bunga_server_to_client_t *self_p);

void bunga_server_to_client_encode_repeated_inner(
    struct pbtools_encoder_t *encoder_p,
    int field_number,
    struct bunga_server_to_client_repeated_t *repeated_p);

void bunga_server_to_client_decode_repeated_inner(
    struct pbtools_decoder_t *decoder_p,
    struct pbtools_repeated_info_t *repeated_info_p,
    struct bunga_server_to_client_repeated_t *repeated_p);

#ifdef __cplusplus
}
#endif

#endif
