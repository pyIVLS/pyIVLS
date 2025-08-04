1.  follow instructions from https://gist.github.com/ochococo/8362414fff28fa593bc8f368ba94d46a
	- Instead of 	cd ~/linux-gpib-code/linux-gpib-user
			sudo make install
	use
			cd ~/linux-gpib-code/linux-gpib-user
			./bootstrap
			./configure --sysconfdir=/etc
			sudo make
			sudo make install 
		This will actually make Makefile and will put gpib.conf file in the right place, which is in /etc/gpib.conf and not in /usr/local/etc/gpib.conf

2. To allow access to the gpib without root privileges modify MODE in /etc/udev/rules.d/98-gpib-generic.rules to '0666'

	- ITC503 won’t answer as intended
		-to do that see controlitc.py
		- it has the PyVisa commands needed for controlling

