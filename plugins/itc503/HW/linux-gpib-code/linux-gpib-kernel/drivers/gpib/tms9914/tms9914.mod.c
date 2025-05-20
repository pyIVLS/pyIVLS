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

KSYMTAB_FUNC(tms9914_command, "", "");
KSYMTAB_FUNC(tms9914_board_reset, "_gpl", "");
KSYMTAB_FUNC(tms9914_online, "_gpl", "");
KSYMTAB_FUNC(tms9914_ioport_read_byte, "_gpl", "");
KSYMTAB_FUNC(tms9914_ioport_write_byte, "_gpl", "");
KSYMTAB_FUNC(tms9914_iomem_read_byte, "_gpl", "");
KSYMTAB_FUNC(tms9914_iomem_write_byte, "_gpl", "");
KSYMTAB_FUNC(tms9914_read, "", "");
KSYMTAB_FUNC(tms9914_enable_eos, "", "");
KSYMTAB_FUNC(tms9914_disable_eos, "", "");
KSYMTAB_FUNC(tms9914_serial_poll_response, "", "");
KSYMTAB_FUNC(tms9914_serial_poll_status, "", "");
KSYMTAB_FUNC(tms9914_parallel_poll, "", "");
KSYMTAB_FUNC(tms9914_parallel_poll_configure, "", "");
KSYMTAB_FUNC(tms9914_parallel_poll_response, "", "");
KSYMTAB_FUNC(tms9914_primary_address, "", "");
KSYMTAB_FUNC(tms9914_secondary_address, "", "");
KSYMTAB_FUNC(tms9914_update_status, "", "");
KSYMTAB_FUNC(tms9914_line_status, "", "");
KSYMTAB_FUNC(tms9914_write, "", "");
KSYMTAB_FUNC(tms9914_t1_delay, "_gpl", "");
KSYMTAB_FUNC(tms9914_request_system_control, "_gpl", "");
KSYMTAB_FUNC(tms9914_take_control, "_gpl", "");
KSYMTAB_FUNC(tms9914_take_control_workaround, "_gpl", "");
KSYMTAB_FUNC(tms9914_go_to_standby, "_gpl", "");
KSYMTAB_FUNC(tms9914_interface_clear, "_gpl", "");
KSYMTAB_FUNC(tms9914_remote_enable, "_gpl", "");
KSYMTAB_FUNC(tms9914_return_to_local, "_gpl", "");
KSYMTAB_FUNC(tms9914_set_holdoff_mode, "_gpl", "");
KSYMTAB_FUNC(tms9914_release_holdoff, "_gpl", "");
KSYMTAB_FUNC(tms9914_interrupt, "", "");
KSYMTAB_FUNC(tms9914_interrupt_have_status, "", "");

SYMBOL_CRC(tms9914_command, 0x1e8e9cbd, "");
SYMBOL_CRC(tms9914_board_reset, 0x9fef51c3, "_gpl");
SYMBOL_CRC(tms9914_online, 0xfa3481d3, "_gpl");
SYMBOL_CRC(tms9914_ioport_read_byte, 0x72aafeb4, "_gpl");
SYMBOL_CRC(tms9914_ioport_write_byte, 0xa45179f0, "_gpl");
SYMBOL_CRC(tms9914_iomem_read_byte, 0x350d469e, "_gpl");
SYMBOL_CRC(tms9914_iomem_write_byte, 0xec119222, "_gpl");
SYMBOL_CRC(tms9914_read, 0xf98de409, "");
SYMBOL_CRC(tms9914_enable_eos, 0xf7eee312, "");
SYMBOL_CRC(tms9914_disable_eos, 0x8c3c5f8c, "");
SYMBOL_CRC(tms9914_serial_poll_response, 0x7720daab, "");
SYMBOL_CRC(tms9914_serial_poll_status, 0x4dd441e0, "");
SYMBOL_CRC(tms9914_parallel_poll, 0x566b641e, "");
SYMBOL_CRC(tms9914_parallel_poll_configure, 0x94817651, "");
SYMBOL_CRC(tms9914_parallel_poll_response, 0x73e31e4f, "");
SYMBOL_CRC(tms9914_primary_address, 0x87732c5b, "");
SYMBOL_CRC(tms9914_secondary_address, 0xebedb046, "");
SYMBOL_CRC(tms9914_update_status, 0x9ca53198, "");
SYMBOL_CRC(tms9914_line_status, 0x9a69ad11, "");
SYMBOL_CRC(tms9914_write, 0x819c32d0, "");
SYMBOL_CRC(tms9914_t1_delay, 0x45039683, "_gpl");
SYMBOL_CRC(tms9914_request_system_control, 0x78d8e1dc, "_gpl");
SYMBOL_CRC(tms9914_take_control, 0x7829563e, "_gpl");
SYMBOL_CRC(tms9914_take_control_workaround, 0x80953c7b, "_gpl");
SYMBOL_CRC(tms9914_go_to_standby, 0x044ae45a, "_gpl");
SYMBOL_CRC(tms9914_interface_clear, 0x23b50ecc, "_gpl");
SYMBOL_CRC(tms9914_remote_enable, 0x59da4c2e, "_gpl");
SYMBOL_CRC(tms9914_return_to_local, 0x940d465b, "_gpl");
SYMBOL_CRC(tms9914_set_holdoff_mode, 0xe309d453, "_gpl");
SYMBOL_CRC(tms9914_release_holdoff, 0xea3547b1, "_gpl");
SYMBOL_CRC(tms9914_interrupt, 0xed926613, "");
SYMBOL_CRC(tms9914_interrupt_have_status, 0x52ec7c30, "");

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
	"\x14\x00\x00\x00\x51\x0e\x00\x01"
	"schedule\0\0\0\0"
	"\x1c\x00\x00\x00\xcb\xf6\xfd\xf0"
	"__stack_chk_fail\0\0\0\0"
	"\x18\x00\x00\x00\x75\x79\x48\xfe"
	"init_wait_entry\0"
	"\x24\x00\x00\x00\x70\xce\x5c\xd3"
	"_raw_spin_unlock_irqrestore\0"
	"\x1c\x00\x00\x00\xca\x39\x82\x5b"
	"__x86_return_thunk\0\0"
	"\x18\x00\x00\x00\xf3\x60\x9c\xbe"
	"push_gpib_event\0"
	"\x2c\x00\x00\x00\x61\xe5\x48\xa6"
	"__ubsan_handle_shift_out_of_bounds\0\0"
	"\x18\x00\x00\x00\xd6\xdf\xe3\xea"
	"__const_udelay\0\0"
	"\x24\x00\x00\x00\xf9\xa4\xcc\x66"
	"__x86_indirect_thunk_rcx\0\0\0\0"
	"\x20\x00\x00\x00\x5d\x7b\xc1\xe2"
	"__SCT__might_resched\0\0\0\0"
	"\x18\x00\x00\x00\xde\x9f\x8a\x25"
	"module_layout\0\0\0"
	"\x00\x00\x00\x00\x00\x00\x00\x00";

MODULE_INFO(depends, "gpib_common");


MODULE_INFO(srcversion, "2AE12A36E49CFCB96020460");
