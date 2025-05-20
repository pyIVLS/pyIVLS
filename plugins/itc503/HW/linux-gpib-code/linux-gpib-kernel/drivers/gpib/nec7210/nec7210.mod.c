#include <linux/module.h>
#define INCLUDE_VERMAGIC
#include <linux/build-salt.h>
#include <linux/elfnote-lto.h>
#include <linux/export-internal.h>
#include <linux/vermagic.h>
#include <linux/compiler.h>

#ifdef CONFIG_UNWINDER_ORC
#include <asm/orc_header.h>
ORC_HEADER;
#endif

BUILD_SALT;
BUILD_LTO_INFO;

MODULE_INFO(vermagic, VERMAGIC_STRING);
MODULE_INFO(name, KBUILD_MODNAME);

__visible struct module __this_module
__section(".gnu.linkonce.this_module") = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};

#ifdef CONFIG_MITIGATION_RETPOLINE
MODULE_INFO(retpoline, "Y");
#endif

KSYMTAB_FUNC(nec7210_command, "", "");
KSYMTAB_FUNC(nec7210_board_reset, "", "");
KSYMTAB_FUNC(nec7210_board_online, "", "");
KSYMTAB_FUNC(nec7210_ioport_read_byte, "", "");
KSYMTAB_FUNC(nec7210_ioport_write_byte, "", "");
KSYMTAB_FUNC(nec7210_iomem_read_byte, "", "");
KSYMTAB_FUNC(nec7210_iomem_write_byte, "", "");
KSYMTAB_FUNC(nec7210_locking_ioport_read_byte, "", "");
KSYMTAB_FUNC(nec7210_locking_ioport_write_byte, "", "");
KSYMTAB_FUNC(nec7210_locking_iomem_read_byte, "", "");
KSYMTAB_FUNC(nec7210_locking_iomem_write_byte, "", "");
KSYMTAB_FUNC(nec7210_read, "", "");
KSYMTAB_FUNC(nec7210_enable_eos, "", "");
KSYMTAB_FUNC(nec7210_disable_eos, "", "");
KSYMTAB_FUNC(nec7210_serial_poll_response, "", "");
KSYMTAB_FUNC(nec7210_serial_poll_status, "", "");
KSYMTAB_FUNC(nec7210_parallel_poll_configure, "", "");
KSYMTAB_FUNC(nec7210_parallel_poll_response, "", "");
KSYMTAB_FUNC(nec7210_parallel_poll, "", "");
KSYMTAB_FUNC(nec7210_primary_address, "", "");
KSYMTAB_FUNC(nec7210_secondary_address, "", "");
KSYMTAB_FUNC(nec7210_update_status, "", "");
KSYMTAB_FUNC(nec7210_update_status_nolock, "", "");
KSYMTAB_FUNC(nec7210_set_reg_bits, "", "");
KSYMTAB_FUNC(nec7210_set_handshake_mode, "", "");
KSYMTAB_FUNC(nec7210_read_data_in, "", "");
KSYMTAB_FUNC(nec7210_write, "", "");
KSYMTAB_FUNC(nec7210_t1_delay, "", "");
KSYMTAB_FUNC(nec7210_request_system_control, "", "");
KSYMTAB_FUNC(nec7210_take_control, "", "");
KSYMTAB_FUNC(nec7210_go_to_standby, "", "");
KSYMTAB_FUNC(nec7210_interface_clear, "", "");
KSYMTAB_FUNC(nec7210_remote_enable, "", "");
KSYMTAB_FUNC(nec7210_release_rfd_holdoff, "", "");
KSYMTAB_FUNC(nec7210_return_to_local, "", "");
KSYMTAB_FUNC(nec7210_interrupt, "", "");
KSYMTAB_FUNC(nec7210_interrupt_have_status, "", "");

SYMBOL_CRC(nec7210_command, 0xf8af60bc, "");
SYMBOL_CRC(nec7210_board_reset, 0xf7dfce5d, "");
SYMBOL_CRC(nec7210_board_online, 0x3e81e54e, "");
SYMBOL_CRC(nec7210_ioport_read_byte, 0x5b4eb6c7, "");
SYMBOL_CRC(nec7210_ioport_write_byte, 0x9e45d2bd, "");
SYMBOL_CRC(nec7210_iomem_read_byte, 0xd270e0d2, "");
SYMBOL_CRC(nec7210_iomem_write_byte, 0xdbc67765, "");
SYMBOL_CRC(nec7210_locking_ioport_read_byte, 0x630728a4, "");
SYMBOL_CRC(nec7210_locking_ioport_write_byte, 0x30c200dc, "");
SYMBOL_CRC(nec7210_locking_iomem_read_byte, 0x432c4770, "");
SYMBOL_CRC(nec7210_locking_iomem_write_byte, 0x8d7e5c8d, "");
SYMBOL_CRC(nec7210_read, 0x39fa26f4, "");
SYMBOL_CRC(nec7210_enable_eos, 0x141c8322, "");
SYMBOL_CRC(nec7210_disable_eos, 0xe8d82aeb, "");
SYMBOL_CRC(nec7210_serial_poll_response, 0x81067565, "");
SYMBOL_CRC(nec7210_serial_poll_status, 0xcecd90a8, "");
SYMBOL_CRC(nec7210_parallel_poll_configure, 0x29088362, "");
SYMBOL_CRC(nec7210_parallel_poll_response, 0x0a34e90c, "");
SYMBOL_CRC(nec7210_parallel_poll, 0xf4af1495, "");
SYMBOL_CRC(nec7210_primary_address, 0x6fd5dfac, "");
SYMBOL_CRC(nec7210_secondary_address, 0xc0871697, "");
SYMBOL_CRC(nec7210_update_status, 0x03dc4932, "");
SYMBOL_CRC(nec7210_update_status_nolock, 0x8cca6b20, "");
SYMBOL_CRC(nec7210_set_reg_bits, 0x778ad7ed, "");
SYMBOL_CRC(nec7210_set_handshake_mode, 0xfdae0c9d, "");
SYMBOL_CRC(nec7210_read_data_in, 0xf16bde82, "");
SYMBOL_CRC(nec7210_write, 0xb5939522, "");
SYMBOL_CRC(nec7210_t1_delay, 0xe0523262, "");
SYMBOL_CRC(nec7210_request_system_control, 0xb13233d8, "");
SYMBOL_CRC(nec7210_take_control, 0xe73dfa9e, "");
SYMBOL_CRC(nec7210_go_to_standby, 0x69a0a77c, "");
SYMBOL_CRC(nec7210_interface_clear, 0x87a145df, "");
SYMBOL_CRC(nec7210_remote_enable, 0xbb388460, "");
SYMBOL_CRC(nec7210_release_rfd_holdoff, 0x47d46f6d, "");
SYMBOL_CRC(nec7210_return_to_local, 0x817fa0ec, "");
SYMBOL_CRC(nec7210_interrupt, 0xfbc8091c, "");
SYMBOL_CRC(nec7210_interrupt_have_status, 0x21fe805f, "");

static const char ____versions[]
__used __section("__versions") =
	"\x14\x00\x00\x00\xbf\x0f\x54\x92"
	"finish_wait\0"
	"\x20\x00\x00\x00\x95\xd4\x26\x8c"
	"prepare_to_wait_event\0\0\0"
	"\x14\x00\x00\x00\x44\x43\x96\xe2"
	"__wake_up\0\0\0"
	"\x20\x00\x00\x00\x0b\x05\xdb\x34"
	"_raw_spin_lock_irqsave\0\0"
	"\x14\x00\x00\x00\xbb\x6d\xfb\xbd"
	"__fentry__\0\0"
	"\x24\x00\x00\x00\x97\x70\x48\x65"
	"__x86_indirect_thunk_rax\0\0\0\0"
	"\x10\x00\x00\x00\x7e\x3a\x2c\x12"
	"_printk\0"
	"\x1c\x00\x00\x00\xad\x8a\xdd\x8d"
	"schedule_timeout\0\0\0\0"
	"\x14\x00\x00\x00\x51\x0e\x00\x01"
	"schedule\0\0\0\0"
	"\x1c\x00\x00\x00\xcb\xf6\xfd\xf0"
	"__stack_chk_fail\0\0\0\0"
	"\x18\x00\x00\x00\xa2\xe8\x6d\x4e"
	"const_pcpu_hot\0\0"
	"\x28\x00\x00\x00\xb3\x1c\xa2\x87"
	"__ubsan_handle_out_of_bounds\0\0\0\0"
	"\x18\x00\x00\x00\x75\x79\x48\xfe"
	"init_wait_entry\0"
	"\x24\x00\x00\x00\x70\xce\x5c\xd3"
	"_raw_spin_unlock_irqrestore\0"
	"\x1c\x00\x00\x00\xca\x39\x82\x5b"
	"__x86_return_thunk\0\0"
	"\x18\x00\x00\x00\xf3\x60\x9c\xbe"
	"push_gpib_event\0"
	"\x18\x00\x00\x00\xd6\xdf\xe3\xea"
	"__const_udelay\0\0"
	"\x20\x00\x00\x00\x5d\x7b\xc1\xe2"
	"__SCT__might_resched\0\0\0\0"
	"\x18\x00\x00\x00\xde\x9f\x8a\x25"
	"module_layout\0\0\0"
	"\x00\x00\x00\x00\x00\x00\x00\x00";

MODULE_INFO(depends, "gpib_common");


MODULE_INFO(srcversion, "6AEEF3E931FE10B7BF12A2F");
