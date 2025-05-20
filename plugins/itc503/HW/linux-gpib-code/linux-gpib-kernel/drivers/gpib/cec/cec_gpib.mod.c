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



static const char ____versions[]
__used __section("__versions") =
	"\x14\x00\x00\x00\x3b\x4a\x51\xc1"
	"free_irq\0\0\0\0"
	"\x18\x00\x00\x00\xf4\x26\xfa\x39"
	"nec7210_read\0\0\0\0"
	"\x1c\x00\x00\x00\xb8\xc7\x17\xfb"
	"pci_enable_device\0\0\0"
	"\x28\x00\x00\x00\x0c\xe9\x34\x0a"
	"nec7210_parallel_poll_response\0\0"
	"\x1c\x00\x00\x00\x62\x32\x52\xe0"
	"nec7210_t1_delay\0\0\0\0"
	"\x14\x00\x00\x00\x93\x74\xc6\x5d"
	"pci_dev_put\0"
	"\x20\x00\x00\x00\x1f\x5c\x90\xf0"
	"__pci_register_driver\0\0\0"
	"\x1c\x00\x00\x00\x31\xe0\x27\xa7"
	"pci_request_regions\0"
	"\x10\x00\x00\x00\xba\x0c\x7a\x03"
	"kfree\0\0\0"
	"\x20\x00\x00\x00\x79\xc3\x37\xff"
	"gpib_request_pseudo_irq\0"
	"\x20\x00\x00\x00\xac\xdf\xd5\x6f"
	"nec7210_primary_address\0"
	"\x28\x00\x00\x00\xd8\x33\x32\xb1"
	"nec7210_request_system_control\0\0"
	"\x1c\x00\x00\x00\x5d\xce\xdf\xf7"
	"nec7210_board_reset\0"
	"\x20\x00\x00\x00\x0b\x05\xdb\x34"
	"_raw_spin_lock_irqsave\0\0"
	"\x20\x00\x00\x00\x49\x1a\x8f\x46"
	"pci_unregister_driver\0\0\0"
	"\x14\x00\x00\x00\xbb\x6d\xfb\xbd"
	"__fentry__\0\0"
	"\x24\x00\x00\x00\x97\x70\x48\x65"
	"__x86_indirect_thunk_rax\0\0\0\0"
	"\x10\x00\x00\x00\x7e\x3a\x2c\x12"
	"_printk\0"
	"\x20\x00\x00\x00\x8f\x87\x2d\x44"
	"gpib_register_driver\0\0\0\0"
	"\x18\x00\x00\x00\x22\x95\x93\xb5"
	"nec7210_write\0\0\0"
	"\x1c\x00\x00\x00\xeb\x2a\xd8\xe8"
	"nec7210_disable_eos\0"
	"\x24\x00\x00\x00\x97\x16\x87\xc0"
	"nec7210_secondary_address\0\0\0"
	"\x20\x00\x00\x00\x9e\xfa\x3d\xe7"
	"nec7210_take_control\0\0\0\0"
	"\x1c\x00\x00\x00\x1c\x09\xc8\xfb"
	"nec7210_interrupt\0\0\0"
	"\x24\x00\x00\x00\xbd\xd2\x45\x9e"
	"nec7210_ioport_write_byte\0\0\0"
	"\x20\x00\x00\x00\x4e\xe5\x81\x3e"
	"nec7210_board_online\0\0\0\0"
	"\x24\x00\x00\x00\xc7\xb6\x4e\x5b"
	"nec7210_ioport_read_byte\0\0\0\0"
	"\x20\x00\x00\x00\x8e\x83\xd5\x92"
	"request_threaded_irq\0\0\0\0"
	"\x1c\x00\x00\x00\x63\xa5\x03\x4c"
	"random_kmalloc_seed\0"
	"\x20\x00\x00\x00\x7c\xa7\xa0\x69"
	"nec7210_go_to_standby\0\0\0"
	"\x20\x00\x00\x00\xdf\x45\xa1\x87"
	"nec7210_interface_clear\0"
	"\x24\x00\x00\x00\x70\xce\x5c\xd3"
	"_raw_spin_unlock_irqrestore\0"
	"\x20\x00\x00\x00\x95\x14\xaf\xf4"
	"nec7210_parallel_poll\0\0\0"
	"\x1c\x00\x00\x00\xca\x39\x82\x5b"
	"__x86_return_thunk\0\0"
	"\x20\x00\x00\x00\xdc\xbf\x94\x9f"
	"gpib_free_pseudo_irq\0\0\0\0"
	"\x28\x00\x00\x00\x62\x83\x08\x29"
	"nec7210_parallel_poll_configure\0"
	"\x20\x00\x00\x00\xec\xa0\x7f\x81"
	"nec7210_return_to_local\0"
	"\x1c\x00\x00\x00\xc8\x23\x2f\x9d"
	"gpib_pci_get_device\0"
	"\x20\x00\x00\x00\x74\xf9\xc1\x55"
	"gpib_unregister_driver\0\0"
	"\x1c\x00\x00\x00\xcf\x78\x6e\x10"
	"pci_release_regions\0"
	"\x20\x00\x00\x00\x32\x49\xdc\x03"
	"nec7210_update_status\0\0\0"
	"\x20\x00\x00\x00\xee\xfb\xb4\x10"
	"__kmalloc_cache_noprof\0\0"
	"\x1c\x00\x00\x00\x22\x83\x1c\x14"
	"nec7210_enable_eos\0\0"
	"\x24\x00\x00\x00\xa8\x90\xcd\xce"
	"nec7210_serial_poll_status\0\0"
	"\x20\x00\x00\x00\x60\x84\x38\xbb"
	"nec7210_remote_enable\0\0\0"
	"\x18\x00\x00\x00\xbc\x60\xaf\xf8"
	"nec7210_command\0"
	"\x18\x00\x00\x00\xaf\xfc\x16\x7b"
	"kmalloc_caches\0\0"
	"\x28\x00\x00\x00\x65\x75\x06\x81"
	"nec7210_serial_poll_response\0\0\0\0"
	"\x18\x00\x00\x00\xde\x9f\x8a\x25"
	"module_layout\0\0\0"
	"\x00\x00\x00\x00\x00\x00\x00\x00";

MODULE_INFO(depends, "nec7210,gpib_common");

MODULE_ALIAS("pci:v000012FCd00005CECsv*sd00009050bc*sc*i*");

MODULE_INFO(srcversion, "0AA193C0D140E10F77D61A4");
