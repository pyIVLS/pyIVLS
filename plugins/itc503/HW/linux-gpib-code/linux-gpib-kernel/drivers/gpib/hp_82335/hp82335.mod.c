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
	"\x1c\x00\x00\x00\x11\xad\x69\x9a"
	"tms9914_line_status\0"
	"\x24\x00\x00\x00\x22\x92\x11\xec"
	"tms9914_iomem_write_byte\0\0\0\0"
	"\x20\x00\x00\x00\x5b\x46\x0d\x94"
	"tms9914_return_to_local\0"
	"\x28\x00\x00\x00\x30\x7c\xec\x52"
	"tms9914_interrupt_have_status\0\0\0"
	"\x10\x00\x00\x00\x53\x39\xc0\xed"
	"iounmap\0"
	"\x10\x00\x00\x00\xba\x0c\x7a\x03"
	"kfree\0\0\0"
	"\x20\x00\x00\x00\x5a\xe4\x4a\x04"
	"tms9914_go_to_standby\0\0\0"
	"\x20\x00\x00\x00\x0b\x05\xdb\x34"
	"_raw_spin_lock_irqsave\0\0"
	"\x1c\x00\x00\x00\xc2\xc7\x35\x10"
	"__release_region\0\0\0\0"
	"\x14\x00\x00\x00\xbb\x6d\xfb\xbd"
	"__fentry__\0\0"
	"\x20\x00\x00\x00\x3e\x56\x29\x78"
	"tms9914_take_control\0\0\0\0"
	"\x20\x00\x00\x00\xcc\x0e\xb5\x23"
	"tms9914_interface_clear\0"
	"\x24\x00\x00\x00\x97\x70\x48\x65"
	"__x86_indirect_thunk_rax\0\0\0\0"
	"\x10\x00\x00\x00\x7e\x3a\x2c\x12"
	"_printk\0"
	"\x20\x00\x00\x00\x8f\x87\x2d\x44"
	"gpib_register_driver\0\0\0\0"
	"\x18\x00\x00\x00\xbd\x9c\x8e\x1e"
	"tms9914_command\0"
	"\x28\x00\x00\x00\xab\xda\x20\x77"
	"tms9914_serial_poll_response\0\0\0\0"
	"\x20\x00\x00\x00\x2e\x4c\xda\x59"
	"tms9914_remote_enable\0\0\0"
	"\x24\x00\x00\x00\x46\xb0\xed\xeb"
	"tms9914_secondary_address\0\0\0"
	"\x20\x00\x00\x00\x8e\x83\xd5\x92"
	"request_threaded_irq\0\0\0\0"
	"\x1c\x00\x00\x00\x63\xa5\x03\x4c"
	"random_kmalloc_seed\0"
	"\x1c\x00\x00\x00\xc3\x51\xef\x9f"
	"tms9914_board_reset\0"
	"\x10\x00\x00\x00\x09\xcd\x80\xde"
	"ioremap\0"
	"\x24\x00\x00\x00\xe0\x41\xd4\x4d"
	"tms9914_serial_poll_status\0\0"
	"\x24\x00\x00\x00\x70\xce\x5c\xd3"
	"_raw_spin_unlock_irqrestore\0"
	"\x20\x00\x00\x00\x98\x31\xa5\x9c"
	"tms9914_update_status\0\0\0"
	"\x18\x00\x00\x00\xd0\x32\x9c\x81"
	"tms9914_write\0\0\0"
	"\x28\x00\x00\x00\x51\x76\x81\x94"
	"tms9914_parallel_poll_configure\0"
	"\x1c\x00\x00\x00\xca\x39\x82\x5b"
	"__x86_return_thunk\0\0"
	"\x20\x00\x00\x00\x9e\x46\x0d\x35"
	"tms9914_iomem_read_byte\0"
	"\x20\x00\x00\x00\x1e\x64\x6b\x56"
	"tms9914_parallel_poll\0\0\0"
	"\x1c\x00\x00\x00\x83\x96\x03\x45"
	"tms9914_t1_delay\0\0\0\0"
	"\x20\x00\x00\x00\x74\xf9\xc1\x55"
	"gpib_unregister_driver\0\0"
	"\x28\x00\x00\x00\x4f\x1e\xe3\x73"
	"tms9914_parallel_poll_response\0\0"
	"\x20\x00\x00\x00\xee\xfb\xb4\x10"
	"__kmalloc_cache_noprof\0\0"
	"\x20\x00\x00\x00\x5b\x2c\x73\x87"
	"tms9914_primary_address\0"
	"\x18\x00\x00\x00\x09\xe4\x8d\xf9"
	"tms9914_read\0\0\0\0"
	"\x1c\x00\x00\x00\x12\xe3\xee\xf7"
	"tms9914_enable_eos\0\0"
	"\x18\x00\x00\x00\xd3\x81\x34\xfa"
	"tms9914_online\0\0"
	"\x1c\x00\x00\x00\x8c\x5f\x3c\x8c"
	"tms9914_disable_eos\0"
	"\x18\x00\x00\x00\x55\x88\x35\x77"
	"iomem_resource\0\0"
	"\x18\x00\x00\x00\xaf\xfc\x16\x7b"
	"kmalloc_caches\0\0"
	"\x1c\x00\x00\x00\x08\x16\xbd\x85"
	"__request_region\0\0\0\0"
	"\x28\x00\x00\x00\xdc\xe1\xd8\x78"
	"tms9914_request_system_control\0\0"
	"\x18\x00\x00\x00\xde\x9f\x8a\x25"
	"module_layout\0\0\0"
	"\x00\x00\x00\x00\x00\x00\x00\x00";

MODULE_INFO(depends, "tms9914,gpib_common");


MODULE_INFO(srcversion, "9C5AC924FC9111D819AE4B9");
