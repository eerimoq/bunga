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

#include <limits.h>
#include "bunga.h"

#if CHAR_BIT != 8
#    error "Number of bits in a char must be 8."
#endif

void bunga_execute_command_req_init(
    struct bunga_execute_command_req_t *self_p,
    struct pbtools_heap_t *heap_p)
{
    self_p->base.heap_p = heap_p;
    self_p->command_p = "";
}

void bunga_execute_command_req_encode_inner(
    struct pbtools_encoder_t *encoder_p,
    struct bunga_execute_command_req_t *self_p)
{
    pbtools_encoder_write_string(encoder_p, 1, self_p->command_p);
}

void bunga_execute_command_req_decode_inner(
    struct pbtools_decoder_t *decoder_p,
    struct bunga_execute_command_req_t *self_p)
{
    int wire_type;

    while (pbtools_decoder_available(decoder_p)) {
        switch (pbtools_decoder_read_tag(decoder_p, &wire_type)) {

        case 1:
            pbtools_decoder_read_string(decoder_p, wire_type, &self_p->command_p);
            break;

        default:
            pbtools_decoder_skip_field(decoder_p, wire_type);
            break;
        }
    }
}

void bunga_execute_command_req_encode_repeated_inner(
    struct pbtools_encoder_t *encoder_p,
    int field_number,
    struct bunga_execute_command_req_repeated_t *repeated_p)
{
    pbtools_encode_repeated_inner(
        encoder_p,
        field_number,
        (struct pbtools_repeated_message_t *)repeated_p,
        sizeof(struct bunga_execute_command_req_t),
        (pbtools_message_encode_inner_t)bunga_execute_command_req_encode_inner);
}

void bunga_execute_command_req_decode_repeated_inner(
    struct pbtools_decoder_t *decoder_p,
    struct pbtools_repeated_info_t *repeated_info_p,
    struct bunga_execute_command_req_repeated_t *repeated_p)
{
    pbtools_decode_repeated_inner(
        decoder_p,
        repeated_info_p,
        (struct pbtools_repeated_message_t *)repeated_p,
        sizeof(struct bunga_execute_command_req_t),
        (pbtools_message_init_t)bunga_execute_command_req_init,
        (pbtools_message_decode_inner_t)bunga_execute_command_req_decode_inner);
}

struct bunga_execute_command_req_t *
bunga_execute_command_req_new(
    void *workspace_p,
    size_t size)
{
    return (pbtools_message_new(
                workspace_p,
                size,
                sizeof(struct bunga_execute_command_req_t),
                (pbtools_message_init_t)bunga_execute_command_req_init));
}

int bunga_execute_command_req_encode(
    struct bunga_execute_command_req_t *self_p,
    uint8_t *encoded_p,
    size_t size)
{
    return (pbtools_message_encode(
                &self_p->base,
                encoded_p,
                size,
                (pbtools_message_encode_inner_t)bunga_execute_command_req_encode_inner));
}

int bunga_execute_command_req_decode(
    struct bunga_execute_command_req_t *self_p,
    const uint8_t *encoded_p,
    size_t size)
{
    return (pbtools_message_decode(
                &self_p->base,
                encoded_p,
                size,
                (pbtools_message_decode_inner_t)bunga_execute_command_req_decode_inner));
}

void bunga_get_file_req_init(
    struct bunga_get_file_req_t *self_p,
    struct pbtools_heap_t *heap_p)
{
    self_p->base.heap_p = heap_p;
    self_p->path_p = "";
    self_p->response_window_size = 0;
}

void bunga_get_file_req_encode_inner(
    struct pbtools_encoder_t *encoder_p,
    struct bunga_get_file_req_t *self_p)
{
    pbtools_encoder_write_uint32(encoder_p, 2, self_p->response_window_size);
    pbtools_encoder_write_string(encoder_p, 1, self_p->path_p);
}

void bunga_get_file_req_decode_inner(
    struct pbtools_decoder_t *decoder_p,
    struct bunga_get_file_req_t *self_p)
{
    int wire_type;

    while (pbtools_decoder_available(decoder_p)) {
        switch (pbtools_decoder_read_tag(decoder_p, &wire_type)) {

        case 1:
            pbtools_decoder_read_string(decoder_p, wire_type, &self_p->path_p);
            break;

        case 2:
            self_p->response_window_size = pbtools_decoder_read_uint32(decoder_p, wire_type);
            break;

        default:
            pbtools_decoder_skip_field(decoder_p, wire_type);
            break;
        }
    }
}

void bunga_get_file_req_encode_repeated_inner(
    struct pbtools_encoder_t *encoder_p,
    int field_number,
    struct bunga_get_file_req_repeated_t *repeated_p)
{
    pbtools_encode_repeated_inner(
        encoder_p,
        field_number,
        (struct pbtools_repeated_message_t *)repeated_p,
        sizeof(struct bunga_get_file_req_t),
        (pbtools_message_encode_inner_t)bunga_get_file_req_encode_inner);
}

void bunga_get_file_req_decode_repeated_inner(
    struct pbtools_decoder_t *decoder_p,
    struct pbtools_repeated_info_t *repeated_info_p,
    struct bunga_get_file_req_repeated_t *repeated_p)
{
    pbtools_decode_repeated_inner(
        decoder_p,
        repeated_info_p,
        (struct pbtools_repeated_message_t *)repeated_p,
        sizeof(struct bunga_get_file_req_t),
        (pbtools_message_init_t)bunga_get_file_req_init,
        (pbtools_message_decode_inner_t)bunga_get_file_req_decode_inner);
}

struct bunga_get_file_req_t *
bunga_get_file_req_new(
    void *workspace_p,
    size_t size)
{
    return (pbtools_message_new(
                workspace_p,
                size,
                sizeof(struct bunga_get_file_req_t),
                (pbtools_message_init_t)bunga_get_file_req_init));
}

int bunga_get_file_req_encode(
    struct bunga_get_file_req_t *self_p,
    uint8_t *encoded_p,
    size_t size)
{
    return (pbtools_message_encode(
                &self_p->base,
                encoded_p,
                size,
                (pbtools_message_encode_inner_t)bunga_get_file_req_encode_inner));
}

int bunga_get_file_req_decode(
    struct bunga_get_file_req_t *self_p,
    const uint8_t *encoded_p,
    size_t size)
{
    return (pbtools_message_decode(
                &self_p->base,
                encoded_p,
                size,
                (pbtools_message_decode_inner_t)bunga_get_file_req_decode_inner));
}

void bunga_put_file_req_init(
    struct bunga_put_file_req_t *self_p,
    struct pbtools_heap_t *heap_p)
{
    self_p->base.heap_p = heap_p;
    self_p->path_p = "";
    self_p->size = 0;
    pbtools_bytes_init(&self_p->data);
}

void bunga_put_file_req_encode_inner(
    struct pbtools_encoder_t *encoder_p,
    struct bunga_put_file_req_t *self_p)
{
    pbtools_encoder_write_bytes(encoder_p, 3, &self_p->data);
    pbtools_encoder_write_uint64(encoder_p, 2, self_p->size);
    pbtools_encoder_write_string(encoder_p, 1, self_p->path_p);
}

void bunga_put_file_req_decode_inner(
    struct pbtools_decoder_t *decoder_p,
    struct bunga_put_file_req_t *self_p)
{
    int wire_type;

    while (pbtools_decoder_available(decoder_p)) {
        switch (pbtools_decoder_read_tag(decoder_p, &wire_type)) {

        case 1:
            pbtools_decoder_read_string(decoder_p, wire_type, &self_p->path_p);
            break;

        case 2:
            self_p->size = pbtools_decoder_read_uint64(decoder_p, wire_type);
            break;

        case 3:
            pbtools_decoder_read_bytes(decoder_p, wire_type, &self_p->data);
            break;

        default:
            pbtools_decoder_skip_field(decoder_p, wire_type);
            break;
        }
    }
}

void bunga_put_file_req_encode_repeated_inner(
    struct pbtools_encoder_t *encoder_p,
    int field_number,
    struct bunga_put_file_req_repeated_t *repeated_p)
{
    pbtools_encode_repeated_inner(
        encoder_p,
        field_number,
        (struct pbtools_repeated_message_t *)repeated_p,
        sizeof(struct bunga_put_file_req_t),
        (pbtools_message_encode_inner_t)bunga_put_file_req_encode_inner);
}

void bunga_put_file_req_decode_repeated_inner(
    struct pbtools_decoder_t *decoder_p,
    struct pbtools_repeated_info_t *repeated_info_p,
    struct bunga_put_file_req_repeated_t *repeated_p)
{
    pbtools_decode_repeated_inner(
        decoder_p,
        repeated_info_p,
        (struct pbtools_repeated_message_t *)repeated_p,
        sizeof(struct bunga_put_file_req_t),
        (pbtools_message_init_t)bunga_put_file_req_init,
        (pbtools_message_decode_inner_t)bunga_put_file_req_decode_inner);
}

struct bunga_put_file_req_t *
bunga_put_file_req_new(
    void *workspace_p,
    size_t size)
{
    return (pbtools_message_new(
                workspace_p,
                size,
                sizeof(struct bunga_put_file_req_t),
                (pbtools_message_init_t)bunga_put_file_req_init));
}

int bunga_put_file_req_encode(
    struct bunga_put_file_req_t *self_p,
    uint8_t *encoded_p,
    size_t size)
{
    return (pbtools_message_encode(
                &self_p->base,
                encoded_p,
                size,
                (pbtools_message_encode_inner_t)bunga_put_file_req_encode_inner));
}

int bunga_put_file_req_decode(
    struct bunga_put_file_req_t *self_p,
    const uint8_t *encoded_p,
    size_t size)
{
    return (pbtools_message_decode(
                &self_p->base,
                encoded_p,
                size,
                (pbtools_message_decode_inner_t)bunga_put_file_req_decode_inner));
}

void bunga_client_to_server_messages_execute_command_req_init(
    struct bunga_client_to_server_t *self_p)
{
    self_p->messages.choice = bunga_client_to_server_messages_choice_execute_command_req_e;
    bunga_execute_command_req_init(
        &self_p->messages.value.execute_command_req,
        self_p->base.heap_p);
}

void bunga_client_to_server_messages_get_file_req_init(
    struct bunga_client_to_server_t *self_p)
{
    self_p->messages.choice = bunga_client_to_server_messages_choice_get_file_req_e;
    bunga_get_file_req_init(
        &self_p->messages.value.get_file_req,
        self_p->base.heap_p);
}

void bunga_client_to_server_messages_put_file_req_init(
    struct bunga_client_to_server_t *self_p)
{
    self_p->messages.choice = bunga_client_to_server_messages_choice_put_file_req_e;
    bunga_put_file_req_init(
        &self_p->messages.value.put_file_req,
        self_p->base.heap_p);
}

void bunga_client_to_server_messages_encode(
    struct pbtools_encoder_t *encoder_p,
    struct bunga_client_to_server_messages_oneof_t *self_p)
{
    switch (self_p->choice) {

    case bunga_client_to_server_messages_choice_execute_command_req_e:
        pbtools_encoder_sub_message_encode_always(
            encoder_p,
            1,
            &self_p->value.execute_command_req.base,
            (pbtools_message_encode_inner_t)bunga_execute_command_req_encode_inner);
        break;

    case bunga_client_to_server_messages_choice_get_file_req_e:
        pbtools_encoder_sub_message_encode_always(
            encoder_p,
            2,
            &self_p->value.get_file_req.base,
            (pbtools_message_encode_inner_t)bunga_get_file_req_encode_inner);
        break;

    case bunga_client_to_server_messages_choice_put_file_req_e:
        pbtools_encoder_sub_message_encode_always(
            encoder_p,
            3,
            &self_p->value.put_file_req.base,
            (pbtools_message_encode_inner_t)bunga_put_file_req_encode_inner);
        break;

    default:
        break;
    }
}

static void bunga_client_to_server_messages_execute_command_req_decode(
    struct pbtools_decoder_t *decoder_p,
    int wire_type,
    struct bunga_client_to_server_t *self_p)
{
    bunga_client_to_server_messages_execute_command_req_init(self_p);
    pbtools_decoder_sub_message_decode(
        decoder_p,
        wire_type,
        &self_p->messages.value.execute_command_req.base,
        (pbtools_message_decode_inner_t)bunga_execute_command_req_decode_inner);
}

static void bunga_client_to_server_messages_get_file_req_decode(
    struct pbtools_decoder_t *decoder_p,
    int wire_type,
    struct bunga_client_to_server_t *self_p)
{
    bunga_client_to_server_messages_get_file_req_init(self_p);
    pbtools_decoder_sub_message_decode(
        decoder_p,
        wire_type,
        &self_p->messages.value.get_file_req.base,
        (pbtools_message_decode_inner_t)bunga_get_file_req_decode_inner);
}

static void bunga_client_to_server_messages_put_file_req_decode(
    struct pbtools_decoder_t *decoder_p,
    int wire_type,
    struct bunga_client_to_server_t *self_p)
{
    bunga_client_to_server_messages_put_file_req_init(self_p);
    pbtools_decoder_sub_message_decode(
        decoder_p,
        wire_type,
        &self_p->messages.value.put_file_req.base,
        (pbtools_message_decode_inner_t)bunga_put_file_req_decode_inner);
}

void bunga_client_to_server_init(
    struct bunga_client_to_server_t *self_p,
    struct pbtools_heap_t *heap_p)
{
    self_p->base.heap_p = heap_p;
    self_p->messages.choice = 0;
}

void bunga_client_to_server_encode_inner(
    struct pbtools_encoder_t *encoder_p,
    struct bunga_client_to_server_t *self_p)
{
    bunga_client_to_server_messages_encode(encoder_p, &self_p->messages);
}

void bunga_client_to_server_decode_inner(
    struct pbtools_decoder_t *decoder_p,
    struct bunga_client_to_server_t *self_p)
{
    int wire_type;

    while (pbtools_decoder_available(decoder_p)) {
        switch (pbtools_decoder_read_tag(decoder_p, &wire_type)) {

        case 1:
            bunga_client_to_server_messages_execute_command_req_decode(
                decoder_p,
                wire_type,
                self_p);
            break;

        case 2:
            bunga_client_to_server_messages_get_file_req_decode(
                decoder_p,
                wire_type,
                self_p);
            break;

        case 3:
            bunga_client_to_server_messages_put_file_req_decode(
                decoder_p,
                wire_type,
                self_p);
            break;

        default:
            pbtools_decoder_skip_field(decoder_p, wire_type);
            break;
        }
    }
}

void bunga_client_to_server_encode_repeated_inner(
    struct pbtools_encoder_t *encoder_p,
    int field_number,
    struct bunga_client_to_server_repeated_t *repeated_p)
{
    pbtools_encode_repeated_inner(
        encoder_p,
        field_number,
        (struct pbtools_repeated_message_t *)repeated_p,
        sizeof(struct bunga_client_to_server_t),
        (pbtools_message_encode_inner_t)bunga_client_to_server_encode_inner);
}

void bunga_client_to_server_decode_repeated_inner(
    struct pbtools_decoder_t *decoder_p,
    struct pbtools_repeated_info_t *repeated_info_p,
    struct bunga_client_to_server_repeated_t *repeated_p)
{
    pbtools_decode_repeated_inner(
        decoder_p,
        repeated_info_p,
        (struct pbtools_repeated_message_t *)repeated_p,
        sizeof(struct bunga_client_to_server_t),
        (pbtools_message_init_t)bunga_client_to_server_init,
        (pbtools_message_decode_inner_t)bunga_client_to_server_decode_inner);
}

struct bunga_client_to_server_t *
bunga_client_to_server_new(
    void *workspace_p,
    size_t size)
{
    return (pbtools_message_new(
                workspace_p,
                size,
                sizeof(struct bunga_client_to_server_t),
                (pbtools_message_init_t)bunga_client_to_server_init));
}

int bunga_client_to_server_encode(
    struct bunga_client_to_server_t *self_p,
    uint8_t *encoded_p,
    size_t size)
{
    return (pbtools_message_encode(
                &self_p->base,
                encoded_p,
                size,
                (pbtools_message_encode_inner_t)bunga_client_to_server_encode_inner));
}

int bunga_client_to_server_decode(
    struct bunga_client_to_server_t *self_p,
    const uint8_t *encoded_p,
    size_t size)
{
    return (pbtools_message_decode(
                &self_p->base,
                encoded_p,
                size,
                (pbtools_message_decode_inner_t)bunga_client_to_server_decode_inner));
}

void bunga_execute_command_rsp_init(
    struct bunga_execute_command_rsp_t *self_p,
    struct pbtools_heap_t *heap_p)
{
    self_p->base.heap_p = heap_p;
    pbtools_bytes_init(&self_p->output);
    self_p->error_p = "";
}

void bunga_execute_command_rsp_encode_inner(
    struct pbtools_encoder_t *encoder_p,
    struct bunga_execute_command_rsp_t *self_p)
{
    pbtools_encoder_write_string(encoder_p, 2, self_p->error_p);
    pbtools_encoder_write_bytes(encoder_p, 1, &self_p->output);
}

void bunga_execute_command_rsp_decode_inner(
    struct pbtools_decoder_t *decoder_p,
    struct bunga_execute_command_rsp_t *self_p)
{
    int wire_type;

    while (pbtools_decoder_available(decoder_p)) {
        switch (pbtools_decoder_read_tag(decoder_p, &wire_type)) {

        case 1:
            pbtools_decoder_read_bytes(decoder_p, wire_type, &self_p->output);
            break;

        case 2:
            pbtools_decoder_read_string(decoder_p, wire_type, &self_p->error_p);
            break;

        default:
            pbtools_decoder_skip_field(decoder_p, wire_type);
            break;
        }
    }
}

void bunga_execute_command_rsp_encode_repeated_inner(
    struct pbtools_encoder_t *encoder_p,
    int field_number,
    struct bunga_execute_command_rsp_repeated_t *repeated_p)
{
    pbtools_encode_repeated_inner(
        encoder_p,
        field_number,
        (struct pbtools_repeated_message_t *)repeated_p,
        sizeof(struct bunga_execute_command_rsp_t),
        (pbtools_message_encode_inner_t)bunga_execute_command_rsp_encode_inner);
}

void bunga_execute_command_rsp_decode_repeated_inner(
    struct pbtools_decoder_t *decoder_p,
    struct pbtools_repeated_info_t *repeated_info_p,
    struct bunga_execute_command_rsp_repeated_t *repeated_p)
{
    pbtools_decode_repeated_inner(
        decoder_p,
        repeated_info_p,
        (struct pbtools_repeated_message_t *)repeated_p,
        sizeof(struct bunga_execute_command_rsp_t),
        (pbtools_message_init_t)bunga_execute_command_rsp_init,
        (pbtools_message_decode_inner_t)bunga_execute_command_rsp_decode_inner);
}

struct bunga_execute_command_rsp_t *
bunga_execute_command_rsp_new(
    void *workspace_p,
    size_t size)
{
    return (pbtools_message_new(
                workspace_p,
                size,
                sizeof(struct bunga_execute_command_rsp_t),
                (pbtools_message_init_t)bunga_execute_command_rsp_init));
}

int bunga_execute_command_rsp_encode(
    struct bunga_execute_command_rsp_t *self_p,
    uint8_t *encoded_p,
    size_t size)
{
    return (pbtools_message_encode(
                &self_p->base,
                encoded_p,
                size,
                (pbtools_message_encode_inner_t)bunga_execute_command_rsp_encode_inner));
}

int bunga_execute_command_rsp_decode(
    struct bunga_execute_command_rsp_t *self_p,
    const uint8_t *encoded_p,
    size_t size)
{
    return (pbtools_message_decode(
                &self_p->base,
                encoded_p,
                size,
                (pbtools_message_decode_inner_t)bunga_execute_command_rsp_decode_inner));
}

void bunga_log_entry_ind_init(
    struct bunga_log_entry_ind_t *self_p,
    struct pbtools_heap_t *heap_p)
{
    self_p->base.heap_p = heap_p;
    self_p->text.length = 0;
}

void bunga_log_entry_ind_encode_inner(
    struct pbtools_encoder_t *encoder_p,
    struct bunga_log_entry_ind_t *self_p)
{
    pbtools_encoder_write_repeated_string(encoder_p, 1, &self_p->text);
}

void bunga_log_entry_ind_decode_inner(
    struct pbtools_decoder_t *decoder_p,
    struct bunga_log_entry_ind_t *self_p)
{
    int wire_type;
    struct pbtools_repeated_info_t repeated_info_text;

    pbtools_repeated_info_init(&repeated_info_text, 1);

    while (pbtools_decoder_available(decoder_p)) {
        switch (pbtools_decoder_read_tag(decoder_p, &wire_type)) {

        case 1:
            pbtools_repeated_info_decode_string(
                &repeated_info_text,
                decoder_p,
                wire_type);
            break;

        default:
            pbtools_decoder_skip_field(decoder_p, wire_type);
            break;
        }
    }

    pbtools_decoder_decode_repeated_string(
        decoder_p,
        &repeated_info_text,
        &self_p->text);
}

int bunga_log_entry_ind_text_alloc(
    struct bunga_log_entry_ind_t *self_p,
    int length)
{
    return (pbtools_alloc_repeated_string(
                &self_p->base,
                length,
                &self_p->text));
}

void bunga_log_entry_ind_encode_repeated_inner(
    struct pbtools_encoder_t *encoder_p,
    int field_number,
    struct bunga_log_entry_ind_repeated_t *repeated_p)
{
    pbtools_encode_repeated_inner(
        encoder_p,
        field_number,
        (struct pbtools_repeated_message_t *)repeated_p,
        sizeof(struct bunga_log_entry_ind_t),
        (pbtools_message_encode_inner_t)bunga_log_entry_ind_encode_inner);
}

void bunga_log_entry_ind_decode_repeated_inner(
    struct pbtools_decoder_t *decoder_p,
    struct pbtools_repeated_info_t *repeated_info_p,
    struct bunga_log_entry_ind_repeated_t *repeated_p)
{
    pbtools_decode_repeated_inner(
        decoder_p,
        repeated_info_p,
        (struct pbtools_repeated_message_t *)repeated_p,
        sizeof(struct bunga_log_entry_ind_t),
        (pbtools_message_init_t)bunga_log_entry_ind_init,
        (pbtools_message_decode_inner_t)bunga_log_entry_ind_decode_inner);
}

struct bunga_log_entry_ind_t *
bunga_log_entry_ind_new(
    void *workspace_p,
    size_t size)
{
    return (pbtools_message_new(
                workspace_p,
                size,
                sizeof(struct bunga_log_entry_ind_t),
                (pbtools_message_init_t)bunga_log_entry_ind_init));
}

int bunga_log_entry_ind_encode(
    struct bunga_log_entry_ind_t *self_p,
    uint8_t *encoded_p,
    size_t size)
{
    return (pbtools_message_encode(
                &self_p->base,
                encoded_p,
                size,
                (pbtools_message_encode_inner_t)bunga_log_entry_ind_encode_inner));
}

int bunga_log_entry_ind_decode(
    struct bunga_log_entry_ind_t *self_p,
    const uint8_t *encoded_p,
    size_t size)
{
    return (pbtools_message_decode(
                &self_p->base,
                encoded_p,
                size,
                (pbtools_message_decode_inner_t)bunga_log_entry_ind_decode_inner));
}

void bunga_get_file_rsp_init(
    struct bunga_get_file_rsp_t *self_p,
    struct pbtools_heap_t *heap_p)
{
    self_p->base.heap_p = heap_p;
    self_p->size = 0;
    pbtools_bytes_init(&self_p->data);
    self_p->error_p = "";
}

void bunga_get_file_rsp_encode_inner(
    struct pbtools_encoder_t *encoder_p,
    struct bunga_get_file_rsp_t *self_p)
{
    pbtools_encoder_write_string(encoder_p, 3, self_p->error_p);
    pbtools_encoder_write_bytes(encoder_p, 2, &self_p->data);
    pbtools_encoder_write_uint64(encoder_p, 1, self_p->size);
}

void bunga_get_file_rsp_decode_inner(
    struct pbtools_decoder_t *decoder_p,
    struct bunga_get_file_rsp_t *self_p)
{
    int wire_type;

    while (pbtools_decoder_available(decoder_p)) {
        switch (pbtools_decoder_read_tag(decoder_p, &wire_type)) {

        case 1:
            self_p->size = pbtools_decoder_read_uint64(decoder_p, wire_type);
            break;

        case 2:
            pbtools_decoder_read_bytes(decoder_p, wire_type, &self_p->data);
            break;

        case 3:
            pbtools_decoder_read_string(decoder_p, wire_type, &self_p->error_p);
            break;

        default:
            pbtools_decoder_skip_field(decoder_p, wire_type);
            break;
        }
    }
}

void bunga_get_file_rsp_encode_repeated_inner(
    struct pbtools_encoder_t *encoder_p,
    int field_number,
    struct bunga_get_file_rsp_repeated_t *repeated_p)
{
    pbtools_encode_repeated_inner(
        encoder_p,
        field_number,
        (struct pbtools_repeated_message_t *)repeated_p,
        sizeof(struct bunga_get_file_rsp_t),
        (pbtools_message_encode_inner_t)bunga_get_file_rsp_encode_inner);
}

void bunga_get_file_rsp_decode_repeated_inner(
    struct pbtools_decoder_t *decoder_p,
    struct pbtools_repeated_info_t *repeated_info_p,
    struct bunga_get_file_rsp_repeated_t *repeated_p)
{
    pbtools_decode_repeated_inner(
        decoder_p,
        repeated_info_p,
        (struct pbtools_repeated_message_t *)repeated_p,
        sizeof(struct bunga_get_file_rsp_t),
        (pbtools_message_init_t)bunga_get_file_rsp_init,
        (pbtools_message_decode_inner_t)bunga_get_file_rsp_decode_inner);
}

struct bunga_get_file_rsp_t *
bunga_get_file_rsp_new(
    void *workspace_p,
    size_t size)
{
    return (pbtools_message_new(
                workspace_p,
                size,
                sizeof(struct bunga_get_file_rsp_t),
                (pbtools_message_init_t)bunga_get_file_rsp_init));
}

int bunga_get_file_rsp_encode(
    struct bunga_get_file_rsp_t *self_p,
    uint8_t *encoded_p,
    size_t size)
{
    return (pbtools_message_encode(
                &self_p->base,
                encoded_p,
                size,
                (pbtools_message_encode_inner_t)bunga_get_file_rsp_encode_inner));
}

int bunga_get_file_rsp_decode(
    struct bunga_get_file_rsp_t *self_p,
    const uint8_t *encoded_p,
    size_t size)
{
    return (pbtools_message_decode(
                &self_p->base,
                encoded_p,
                size,
                (pbtools_message_decode_inner_t)bunga_get_file_rsp_decode_inner));
}

void bunga_put_file_rsp_init(
    struct bunga_put_file_rsp_t *self_p,
    struct pbtools_heap_t *heap_p)
{
    self_p->base.heap_p = heap_p;
    self_p->window_size = 0;
    self_p->error_p = "";
}

void bunga_put_file_rsp_encode_inner(
    struct pbtools_encoder_t *encoder_p,
    struct bunga_put_file_rsp_t *self_p)
{
    pbtools_encoder_write_string(encoder_p, 2, self_p->error_p);
    pbtools_encoder_write_uint32(encoder_p, 1, self_p->window_size);
}

void bunga_put_file_rsp_decode_inner(
    struct pbtools_decoder_t *decoder_p,
    struct bunga_put_file_rsp_t *self_p)
{
    int wire_type;

    while (pbtools_decoder_available(decoder_p)) {
        switch (pbtools_decoder_read_tag(decoder_p, &wire_type)) {

        case 1:
            self_p->window_size = pbtools_decoder_read_uint32(decoder_p, wire_type);
            break;

        case 2:
            pbtools_decoder_read_string(decoder_p, wire_type, &self_p->error_p);
            break;

        default:
            pbtools_decoder_skip_field(decoder_p, wire_type);
            break;
        }
    }
}

void bunga_put_file_rsp_encode_repeated_inner(
    struct pbtools_encoder_t *encoder_p,
    int field_number,
    struct bunga_put_file_rsp_repeated_t *repeated_p)
{
    pbtools_encode_repeated_inner(
        encoder_p,
        field_number,
        (struct pbtools_repeated_message_t *)repeated_p,
        sizeof(struct bunga_put_file_rsp_t),
        (pbtools_message_encode_inner_t)bunga_put_file_rsp_encode_inner);
}

void bunga_put_file_rsp_decode_repeated_inner(
    struct pbtools_decoder_t *decoder_p,
    struct pbtools_repeated_info_t *repeated_info_p,
    struct bunga_put_file_rsp_repeated_t *repeated_p)
{
    pbtools_decode_repeated_inner(
        decoder_p,
        repeated_info_p,
        (struct pbtools_repeated_message_t *)repeated_p,
        sizeof(struct bunga_put_file_rsp_t),
        (pbtools_message_init_t)bunga_put_file_rsp_init,
        (pbtools_message_decode_inner_t)bunga_put_file_rsp_decode_inner);
}

struct bunga_put_file_rsp_t *
bunga_put_file_rsp_new(
    void *workspace_p,
    size_t size)
{
    return (pbtools_message_new(
                workspace_p,
                size,
                sizeof(struct bunga_put_file_rsp_t),
                (pbtools_message_init_t)bunga_put_file_rsp_init));
}

int bunga_put_file_rsp_encode(
    struct bunga_put_file_rsp_t *self_p,
    uint8_t *encoded_p,
    size_t size)
{
    return (pbtools_message_encode(
                &self_p->base,
                encoded_p,
                size,
                (pbtools_message_encode_inner_t)bunga_put_file_rsp_encode_inner));
}

int bunga_put_file_rsp_decode(
    struct bunga_put_file_rsp_t *self_p,
    const uint8_t *encoded_p,
    size_t size)
{
    return (pbtools_message_decode(
                &self_p->base,
                encoded_p,
                size,
                (pbtools_message_decode_inner_t)bunga_put_file_rsp_decode_inner));
}

void bunga_server_to_client_messages_execute_command_rsp_init(
    struct bunga_server_to_client_t *self_p)
{
    self_p->messages.choice = bunga_server_to_client_messages_choice_execute_command_rsp_e;
    bunga_execute_command_rsp_init(
        &self_p->messages.value.execute_command_rsp,
        self_p->base.heap_p);
}

void bunga_server_to_client_messages_log_entry_ind_init(
    struct bunga_server_to_client_t *self_p)
{
    self_p->messages.choice = bunga_server_to_client_messages_choice_log_entry_ind_e;
    bunga_log_entry_ind_init(
        &self_p->messages.value.log_entry_ind,
        self_p->base.heap_p);
}

void bunga_server_to_client_messages_get_file_rsp_init(
    struct bunga_server_to_client_t *self_p)
{
    self_p->messages.choice = bunga_server_to_client_messages_choice_get_file_rsp_e;
    bunga_get_file_rsp_init(
        &self_p->messages.value.get_file_rsp,
        self_p->base.heap_p);
}

void bunga_server_to_client_messages_put_file_rsp_init(
    struct bunga_server_to_client_t *self_p)
{
    self_p->messages.choice = bunga_server_to_client_messages_choice_put_file_rsp_e;
    bunga_put_file_rsp_init(
        &self_p->messages.value.put_file_rsp,
        self_p->base.heap_p);
}

void bunga_server_to_client_messages_encode(
    struct pbtools_encoder_t *encoder_p,
    struct bunga_server_to_client_messages_oneof_t *self_p)
{
    switch (self_p->choice) {

    case bunga_server_to_client_messages_choice_execute_command_rsp_e:
        pbtools_encoder_sub_message_encode_always(
            encoder_p,
            1,
            &self_p->value.execute_command_rsp.base,
            (pbtools_message_encode_inner_t)bunga_execute_command_rsp_encode_inner);
        break;

    case bunga_server_to_client_messages_choice_log_entry_ind_e:
        pbtools_encoder_sub_message_encode_always(
            encoder_p,
            2,
            &self_p->value.log_entry_ind.base,
            (pbtools_message_encode_inner_t)bunga_log_entry_ind_encode_inner);
        break;

    case bunga_server_to_client_messages_choice_get_file_rsp_e:
        pbtools_encoder_sub_message_encode_always(
            encoder_p,
            3,
            &self_p->value.get_file_rsp.base,
            (pbtools_message_encode_inner_t)bunga_get_file_rsp_encode_inner);
        break;

    case bunga_server_to_client_messages_choice_put_file_rsp_e:
        pbtools_encoder_sub_message_encode_always(
            encoder_p,
            4,
            &self_p->value.put_file_rsp.base,
            (pbtools_message_encode_inner_t)bunga_put_file_rsp_encode_inner);
        break;

    default:
        break;
    }
}

static void bunga_server_to_client_messages_execute_command_rsp_decode(
    struct pbtools_decoder_t *decoder_p,
    int wire_type,
    struct bunga_server_to_client_t *self_p)
{
    bunga_server_to_client_messages_execute_command_rsp_init(self_p);
    pbtools_decoder_sub_message_decode(
        decoder_p,
        wire_type,
        &self_p->messages.value.execute_command_rsp.base,
        (pbtools_message_decode_inner_t)bunga_execute_command_rsp_decode_inner);
}

static void bunga_server_to_client_messages_log_entry_ind_decode(
    struct pbtools_decoder_t *decoder_p,
    int wire_type,
    struct bunga_server_to_client_t *self_p)
{
    bunga_server_to_client_messages_log_entry_ind_init(self_p);
    pbtools_decoder_sub_message_decode(
        decoder_p,
        wire_type,
        &self_p->messages.value.log_entry_ind.base,
        (pbtools_message_decode_inner_t)bunga_log_entry_ind_decode_inner);
}

static void bunga_server_to_client_messages_get_file_rsp_decode(
    struct pbtools_decoder_t *decoder_p,
    int wire_type,
    struct bunga_server_to_client_t *self_p)
{
    bunga_server_to_client_messages_get_file_rsp_init(self_p);
    pbtools_decoder_sub_message_decode(
        decoder_p,
        wire_type,
        &self_p->messages.value.get_file_rsp.base,
        (pbtools_message_decode_inner_t)bunga_get_file_rsp_decode_inner);
}

static void bunga_server_to_client_messages_put_file_rsp_decode(
    struct pbtools_decoder_t *decoder_p,
    int wire_type,
    struct bunga_server_to_client_t *self_p)
{
    bunga_server_to_client_messages_put_file_rsp_init(self_p);
    pbtools_decoder_sub_message_decode(
        decoder_p,
        wire_type,
        &self_p->messages.value.put_file_rsp.base,
        (pbtools_message_decode_inner_t)bunga_put_file_rsp_decode_inner);
}

void bunga_server_to_client_init(
    struct bunga_server_to_client_t *self_p,
    struct pbtools_heap_t *heap_p)
{
    self_p->base.heap_p = heap_p;
    self_p->messages.choice = 0;
}

void bunga_server_to_client_encode_inner(
    struct pbtools_encoder_t *encoder_p,
    struct bunga_server_to_client_t *self_p)
{
    bunga_server_to_client_messages_encode(encoder_p, &self_p->messages);
}

void bunga_server_to_client_decode_inner(
    struct pbtools_decoder_t *decoder_p,
    struct bunga_server_to_client_t *self_p)
{
    int wire_type;

    while (pbtools_decoder_available(decoder_p)) {
        switch (pbtools_decoder_read_tag(decoder_p, &wire_type)) {

        case 1:
            bunga_server_to_client_messages_execute_command_rsp_decode(
                decoder_p,
                wire_type,
                self_p);
            break;

        case 2:
            bunga_server_to_client_messages_log_entry_ind_decode(
                decoder_p,
                wire_type,
                self_p);
            break;

        case 3:
            bunga_server_to_client_messages_get_file_rsp_decode(
                decoder_p,
                wire_type,
                self_p);
            break;

        case 4:
            bunga_server_to_client_messages_put_file_rsp_decode(
                decoder_p,
                wire_type,
                self_p);
            break;

        default:
            pbtools_decoder_skip_field(decoder_p, wire_type);
            break;
        }
    }
}

void bunga_server_to_client_encode_repeated_inner(
    struct pbtools_encoder_t *encoder_p,
    int field_number,
    struct bunga_server_to_client_repeated_t *repeated_p)
{
    pbtools_encode_repeated_inner(
        encoder_p,
        field_number,
        (struct pbtools_repeated_message_t *)repeated_p,
        sizeof(struct bunga_server_to_client_t),
        (pbtools_message_encode_inner_t)bunga_server_to_client_encode_inner);
}

void bunga_server_to_client_decode_repeated_inner(
    struct pbtools_decoder_t *decoder_p,
    struct pbtools_repeated_info_t *repeated_info_p,
    struct bunga_server_to_client_repeated_t *repeated_p)
{
    pbtools_decode_repeated_inner(
        decoder_p,
        repeated_info_p,
        (struct pbtools_repeated_message_t *)repeated_p,
        sizeof(struct bunga_server_to_client_t),
        (pbtools_message_init_t)bunga_server_to_client_init,
        (pbtools_message_decode_inner_t)bunga_server_to_client_decode_inner);
}

struct bunga_server_to_client_t *
bunga_server_to_client_new(
    void *workspace_p,
    size_t size)
{
    return (pbtools_message_new(
                workspace_p,
                size,
                sizeof(struct bunga_server_to_client_t),
                (pbtools_message_init_t)bunga_server_to_client_init));
}

int bunga_server_to_client_encode(
    struct bunga_server_to_client_t *self_p,
    uint8_t *encoded_p,
    size_t size)
{
    return (pbtools_message_encode(
                &self_p->base,
                encoded_p,
                size,
                (pbtools_message_encode_inner_t)bunga_server_to_client_encode_inner));
}

int bunga_server_to_client_decode(
    struct bunga_server_to_client_t *self_p,
    const uint8_t *encoded_p,
    size_t size)
{
    return (pbtools_message_decode(
                &self_p->base,
                encoded_p,
                size,
                (pbtools_message_decode_inner_t)bunga_server_to_client_decode_inner));
}
