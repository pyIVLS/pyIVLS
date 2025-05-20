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

KSYMTAB_FUNC(gpib_register_driver, "", "");
KSYMTAB_FUNC(gpib_unregister_driver, "", "");
KSYMTAB_FUNC(gpib_pci_get_device, "", "");
KSYMTAB_FUNC(gpib_pci_get_subsys, "", "");
KSYMTAB_FUNC(gpib_match_device_path, "", "");
KSYMTAB_FUNC(writeb_wrapper, "", "");
KSYMTAB_FUNC(readb_wrapper, "", "");
KSYMTAB_FUNC(outb_wrapper, "", "");
KSYMTAB_FUNC(inb_wrapper, "", "");
KSYMTAB_FUNC(writew_wrapper, "", "");
KSYMTAB_FUNC(readw_wrapper, "", "");
KSYMTAB_FUNC(outw_wrapper, "", "");
KSYMTAB_FUNC(inw_wrapper, "", "");
KSYMTAB_FUNC(gpib_request_pseudo_irq, "", "");
KSYMTAB_FUNC(gpib_free_pseudo_irq, "", "");
KSYMTAB_FUNC(push_gpib_event, "", "");

SYMBOL_CRC(gpib_register_driver, 0x442d878f, "");
SYMBOL_CRC(gpib_unregister_driver, 0x55c1f974, "");
SYMBOL_CRC(gpib_pci_get_device, 0x9d2f23c8, "");
SYMBOL_CRC(gpib_pci_get_subsys, 0x20db315a, "");
SYMBOL_CRC(gpib_match_device_path, 0x314facd7, "");
SYMBOL_CRC(writeb_wrapper, 0x92df39db, "");
SYMBOL_CRC(readb_wrapper, 0x69279cb9, "");
SYMBOL_CRC(outb_wrapper, 0x881e5c01, "");
SYMBOL_CRC(inb_wrapper, 0x868fcdb4, "");
SYMBOL_CRC(writew_wrapper, 0xdebed785, "");
SYMBOL_CRC(readw_wrapper, 0xafe00970, "");
SYMBOL_CRC(outw_wrapper, 0xc47fb25f, "");
SYMBOL_CRC(inw_wrapper, 0x4048587d, "");
SYMBOL_CRC(gpib_request_pseudo_irq, 0xff37c379, "");
SYMBOL_CRC(gpib_free_pseudo_irq, 0x9f94bfdc, "");
SYMBOL_CRC(push_gpib_event, 0xbe9c60f3, "");

static const char ____versions[]
__used __section("__versions") =
	"\x18\x00\x00\x00\x88\x2c\x5e\xf1"
	"try_module_get\0\0"
	"\x1c\x00\x00\x00\x48\x9f\xdb\x88"
	"__check_object_size\0"
	"\x14\x00\x00\x00\xd0\x6b\x7d\x9e"
	"__udelay\0\0\0\0"
	"\x18\x00\x00\x00\xc2\x9c\xc4\x13"
	"_copy_from_user\0"
	"\x14\x00\x00\x00\x6e\x4a\x6e\x65"
	"snprintf\0\0\0\0"
	"\x14\x00\x00\x00\xbf\x0f\x54\x92"
	"finish_wait\0"
	"\x18\x00\x00\x00\x1c\xcf\x21\xb2"
	"pci_get_device\0\0"
	"\x18\x00\x00\x00\xbd\xb5\xbf\x6f"
	"class_destroy\0\0\0"
	"\x10\x00\x00\x00\xba\x0c\x7a\x03"
	"kfree\0\0\0"
	"\x1c\x00\x00\x00\xf7\xd2\x15\x6f"
	"kobject_get_path\0\0\0\0"
	"\x20\x00\x00\x00\x95\xd4\x26\x8c"
	"prepare_to_wait_event\0\0\0"
	"\x1c\x00\x00\x00\x6e\x64\xf7\xb3"
	"kthread_should_stop\0"
	"\x1c\x00\x00\x00\xdc\x90\xee\x82"
	"timer_delete_sync\0\0\0"
	"\x14\x00\x00\x00\x44\x43\x96\xe2"
	"__wake_up\0\0\0"
	"\x20\x00\x00\x00\x0b\x05\xdb\x34"
	"_raw_spin_lock_irqsave\0\0"
	"\x18\x00\x00\x00\x64\xbd\x8f\xba"
	"_raw_spin_lock\0\0"
	"\x14\x00\x00\x00\xbb\x6d\xfb\xbd"
	"__fentry__\0\0"
	"\x18\x00\x00\x00\x89\xbc\x9a\x96"
	"wake_up_process\0"
	"\x24\x00\x00\x00\x97\x70\x48\x65"
	"__x86_indirect_thunk_rax\0\0\0\0"
	"\x10\x00\x00\x00\x7e\x3a\x2c\x12"
	"_printk\0"
	"\x14\x00\x00\x00\x51\x0e\x00\x01"
	"schedule\0\0\0\0"
	"\x1c\x00\x00\x00\xcb\xf6\xfd\xf0"
	"__stack_chk_fail\0\0\0\0"
	"\x20\x00\x00\x00\xe9\x0d\x1d\x44"
	"__kmalloc_large_noprof\0\0"
	"\x10\x00\x00\x00\x94\xb6\x16\xa9"
	"strnlen\0"
	"\x18\x00\x00\x00\xa2\xe8\x6d\x4e"
	"const_pcpu_hot\0\0"
	"\x10\x00\x00\x00\x89\xbc\xcb\xc6"
	"capable\0"
	"\x14\x00\x00\x00\x6b\x5c\x5d\x8f"
	"module_put\0\0"
	"\x28\x00\x00\x00\xb3\x1c\xa2\x87"
	"__ubsan_handle_out_of_bounds\0\0\0\0"
	"\x18\x00\x00\x00\x75\x79\x48\xfe"
	"init_wait_entry\0"
	"\x14\x00\x00\x00\x38\x24\xc3\xb0"
	"_dev_err\0\0\0\0"
	"\x14\x00\x00\x00\xb8\x83\x8c\xc3"
	"mod_timer\0\0\0"
	"\x18\x00\x00\x00\x91\x7d\x78\x49"
	"device_create\0\0\0"
	"\x18\x00\x00\x00\x4f\x1e\x1f\x59"
	"class_create\0\0\0\0"
	"\x1c\x00\x00\x00\x63\xa5\x03\x4c"
	"random_kmalloc_seed\0"
	"\x18\x00\x00\x00\xa9\xa1\x2f\x1b"
	"vmalloc_noprof\0\0"
	"\x14\x00\x00\x00\x4b\x8d\xfa\x4d"
	"mutex_lock\0\0"
	"\x18\x00\x00\x00\x55\xc6\x6d\xcc"
	"kthread_stop\0\0\0\0"
	"\x18\x00\x00\x00\x9f\x0c\xfb\xce"
	"__mutex_init\0\0\0\0"
	"\x24\x00\x00\x00\x75\x08\x94\x89"
	"mutex_lock_interruptible\0\0\0\0"
	"\x18\x00\x00\x00\xb5\x79\xca\x75"
	"__fortify_panic\0"
	"\x24\x00\x00\x00\x70\xce\x5c\xd3"
	"_raw_spin_unlock_irqrestore\0"
	"\x18\x00\x00\x00\xf0\xd5\xca\x1e"
	"pci_get_subsys\0\0"
	"\x10\x00\x00\x00\xc5\x8f\x57\xfb"
	"memset\0\0"
	"\x1c\x00\x00\x00\xca\x39\x82\x5b"
	"__x86_return_thunk\0\0"
	"\x18\x00\x00\x00\xe1\xbe\x10\x6b"
	"_copy_to_user\0\0\0"
	"\x20\x00\x00\x00\x54\xea\xa5\xd9"
	"__init_waitqueue_head\0\0\0"
	"\x10\x00\x00\x00\x5a\x25\xd5\xe2"
	"strcmp\0\0"
	"\x10\x00\x00\x00\xa6\x50\xba\x15"
	"jiffies\0"
	"\x20\x00\x00\x00\xfa\xea\x96\x1a"
	"kthread_create_on_node\0\0"
	"\x10\x00\x00\x00\xa7\xb0\x39\x2d"
	"kstrdup\0"
	"\x10\x00\x00\x00\x97\x82\x9e\x99"
	"vfree\0\0\0"
	"\x18\x00\x00\x00\x38\xf0\x13\x32"
	"mutex_unlock\0\0\0\0"
	"\x18\x00\x00\x00\x39\x63\xf4\xc6"
	"init_timer_key\0\0"
	"\x18\x00\x00\x00\xd6\xdf\xe3\xea"
	"__const_udelay\0\0"
	"\x1c\x00\x00\x00\xfc\x82\xf1\x92"
	"__register_chrdev\0\0\0"
	"\x18\x00\x00\x00\x42\xc4\xff\xb8"
	"device_destroy\0\0"
	"\x20\x00\x00\x00\xee\xfb\xb4\x10"
	"__kmalloc_cache_noprof\0\0"
	"\x1c\x00\x00\x00\x34\x4b\xb5\xb5"
	"_raw_spin_unlock\0\0\0\0"
	"\x20\x00\x00\x00\x5d\x7b\xc1\xe2"
	"__SCT__might_resched\0\0\0\0"
	"\x18\x00\x00\x00\xaf\xfc\x16\x7b"
	"kmalloc_caches\0\0"
	"\x1c\x00\x00\x00\xd8\x23\x4f\xa2"
	"__request_module\0\0\0\0"
	"\x1c\x00\x00\x00\xc0\xfb\xc3\x6b"
	"__unregister_chrdev\0"
	"\x18\x00\x00\x00\xde\x9f\x8a\x25"
	"module_layout\0\0\0"
	"\x00\x00\x00\x00\x00\x00\x00\x00";

MODULE_INFO(depends, "");


MODULE_INFO(srcversion, "67A5460058BF601CAAA3CDF");
