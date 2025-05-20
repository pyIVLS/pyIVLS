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
	"\x14\x00\x00\x00\xbb\x6d\xfb\xbd"
	"__fentry__\0\0"
	"\x1c\x00\x00\x00\xca\x39\x82\x5b"
	"__x86_return_thunk\0\0"
	"\x10\x00\x00\x00\x7e\x3a\x2c\x12"
	"_printk\0"
	"\x0c\x00\x00\x00\x66\x69\x2a\xcf"
	"up\0\0"
	"\x14\x00\x00\x00\x4b\x8d\xfa\x4d"
	"mutex_lock\0\0"
	"\x18\x00\x00\x00\xac\xd5\xa6\x21"
	"usb_alloc_urb\0\0\0"
	"\x18\x00\x00\x00\xf3\xe8\xf3\x11"
	"usb_submit_urb\0\0"
	"\x18\x00\x00\x00\x38\xf0\x13\x32"
	"mutex_unlock\0\0\0\0"
	"\x10\x00\x00\x00\xca\xaf\x26\x66"
	"down\0\0\0\0"
	"\x1c\x00\x00\x00\xdc\x90\xee\x82"
	"timer_delete_sync\0\0\0"
	"\x18\x00\x00\x00\x1e\x83\x0c\x65"
	"usb_free_urb\0\0\0\0"
	"\x1c\x00\x00\x00\x8f\x18\x02\x7f"
	"__msecs_to_jiffies\0\0"
	"\x10\x00\x00\x00\xa6\x50\xba\x15"
	"jiffies\0"
	"\x14\x00\x00\x00\xb8\x83\x8c\xc3"
	"mod_timer\0\0\0"
	"\x18\x00\x00\x00\x2f\x96\x28\x47"
	"usb_kill_urb\0\0\0\0"
	"\x18\x00\x00\x00\xcd\x71\x07\x58"
	"usb_control_msg\0"
	"\x1c\x00\x00\x00\x73\xe5\xd0\x6b"
	"down_interruptible\0\0"
	"\x1c\x00\x00\x00\x63\xa5\x03\x4c"
	"random_kmalloc_seed\0"
	"\x18\x00\x00\x00\xaf\xfc\x16\x7b"
	"kmalloc_caches\0\0"
	"\x20\x00\x00\x00\xee\xfb\xb4\x10"
	"__kmalloc_cache_noprof\0\0"
	"\x10\x00\x00\x00\xba\x0c\x7a\x03"
	"kfree\0\0\0"
	"\x20\x00\x00\x00\x0b\x05\xdb\x34"
	"_raw_spin_lock_irqsave\0\0"
	"\x24\x00\x00\x00\x70\xce\x5c\xd3"
	"_raw_spin_unlock_irqrestore\0"
	"\x14\x00\x00\x00\x44\x43\x96\xe2"
	"__wake_up\0\0\0"
	"\x20\x00\x00\x00\xfe\x05\x50\xcc"
	"msleep_interruptible\0\0\0\0"
	"\x1c\x00\x00\x00\xe8\x75\xa3\xef"
	"usb_register_driver\0"
	"\x20\x00\x00\x00\x8f\x87\x2d\x44"
	"gpib_register_driver\0\0\0\0"
	"\x28\x00\x00\x00\xb3\x1c\xa2\x87"
	"__ubsan_handle_out_of_bounds\0\0\0\0"
	"\x20\x00\x00\x00\x74\xf9\xc1\x55"
	"gpib_unregister_driver\0\0"
	"\x18\x00\x00\x00\x55\xd5\xa4\xe2"
	"usb_deregister\0\0"
	"\x10\x00\x00\x00\xf9\x82\xa4\xf9"
	"msleep\0\0"
	"\x1c\x00\x00\x00\x91\xc9\xc5\x52"
	"__kmalloc_noprof\0\0\0\0"
	"\x1c\x00\x00\x00\xcb\xf6\xfd\xf0"
	"__stack_chk_fail\0\0\0\0"
	"\x14\x00\x00\x00\x20\x5d\xe0\x4a"
	"usb_get_dev\0"
	"\x14\x00\x00\x00\x6e\x4a\x6e\x65"
	"snprintf\0\0\0\0"
	"\x14\x00\x00\x00\xe1\x3e\x82\xc5"
	"usb_put_dev\0"
	"\x14\x00\x00\x00\xb0\x75\x9e\x71"
	"_dev_info\0\0\0"
	"\x18\x00\x00\x00\x9f\x0c\xfb\xce"
	"__mutex_init\0\0\0\0"
	"\x20\x00\x00\x00\xd7\xac\x4f\x31"
	"gpib_match_device_path\0\0"
	"\x20\x00\x00\x00\x2f\xde\x60\x9a"
	"usb_reset_configuration\0"
	"\x18\x00\x00\x00\x39\x63\xf4\xc6"
	"init_timer_key\0\0"
	"\x18\x00\x00\x00\xbf\xd3\x9e\xbb"
	"mutex_trylock\0\0\0"
	"\x10\x00\x00\x00\x38\xdf\xac\x69"
	"memcpy\0\0"
	"\x18\x00\x00\x00\xde\x9f\x8a\x25"
	"module_layout\0\0\0"
	"\x00\x00\x00\x00\x00\x00\x00\x00";

MODULE_INFO(depends, "gpib_common");

MODULE_ALIAS("usb:v3923p702Ad*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v3923p709Bd*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v3923p7618d*dc*dsc*dp*ic*isc*ip*in00*");
MODULE_ALIAS("usb:v3923p725Cd*dc*dsc*dp*ic*isc*ip*in*");
MODULE_ALIAS("usb:v3923p725Dd*dc*dsc*dp*ic*isc*ip*in*");

MODULE_INFO(srcversion, "01145208B2106C5346843DD");
