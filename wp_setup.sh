#!/bin/bash
#Script to stand up a Wordpress instance
remove=""
gethelp(){
	echo "Usage: "
	echo "    Add domain/site: 		sudo ./wp_setup.sh -d <domain>"
	echo "    Remove domain/site:	sudo ./wp_setup.sh -r <domain>"
	echo "    Show this help menu:	./wp_setup.sh -h"
	exit 0
}

apt_update(){
	echo "[*] Updating APT"
	apt-get update
	apt-get upgrade
}

setup_wp(){
	#Updates /etc/host, creates web root, downloads WP source, changes directory permissions.
	export $domain=$1
	echo "Setting up WP for $domain"
	#Update /etc/hosts
	grep "$domain" /etc/hosts
	if [ $? -ne 0 ]
	then
		echo "Updating /etc/hosts"
		echo "127.0.0.1 $domain www.$domain" | tee -a /etc/hosts  2>&1 /dev/null

	else
		continue
	fi
	#Prepare directory
	if [ -d /var/www/$domain ]; 
	then 
		continue
	else 
		echo "Preparing web root directory."
		mkdir /var/www/$domain
	fi
	if [ -f /tmp/latest.tar.gz ]
	then
		rm /tmp/latest.tar.gz
	fi
	wget https://wordpress.org/latest.tar.gz -O /tmp/latest.tar.gz
	sudo tar -C /var/www/$domain -xvzf /tmp/latest.tar.gz
	sudo mv /var/www/$domain/wordpress/* /var/www/$domain/
	sudo rm -rf /var/www/$domain/wordpress/
	sudo chown -R www-data:www-data "/var/www/$domain/"
	sudo chmod -R 755 "/var/www/$domain/"
}

config_apache(){
	#Make HTTPS & change apache configs
	sudo certbot certonly --apache -d www.$domain -d $domain --register-unsafely-without-email

	##Copy config files
	sudo cp /etc/apache2/sites-available/jvetti.tk.conf /etc/apache2/sites-available/$domain.conf 
	sudo cp /etc/apache2/sites-available/jvetti.tk-ssl.conf /etc/apache2/sites-available/$domain-ssl.conf 
	#Replace domain in config files using jvetti.tk as a template
	sed -i "s/jvetti.tk/$domain/g" /etc/apache2/sites-available/$domain.conf 
	sed -i "s/jvetti.tk/$domain/g" /etc/apache2/sites-available/$domain-ssl.conf 
	#Link sites-enabled to sites-available
	ln -s /etc/apache2/sites-available/$domain.conf /etc/apache2/sites-enabled/$domain.conf
	ln -s /etc/apache2/sites-available/$domain-ssl.conf /etc/apache2/sites-enabled/$domain-ssl.conf
	#enable the domain
	sudo a2ensite $domain
}

prepare_db(){
	#Basically just creates a WP user and database named $domain 
	export database_name=$(echo $domain | cut -d '.' -f1)
	#Needs mysql root password and desired DB user password
	read -p "Enter root mysql password: " mysql_root_password
	read -p "Enter wp_user ($database_name) mysql password: " mysql_wp_password
	echo "CREATE DATABASE $database_name;" >> /tmp/batch.sql
	echo "GRANT SELECT,INSERT,UPDATE,DELETE,CREATE,DROP,ALTER ON $database_name.* TO $database_name@localhost IDENTIFIED BY '$mysql_wp_password';" >> /tmp/batch.sql
	echo "FLUSH PRIVILEGES;" >> /tmp/batch.sql
	mysql -u root -p$mysql_root_password < /tmp/batch.sql
	sudo systemctl restart mysql
	#sudo cp /tmp/batch.sql /tmp/batch.backup
	sudo rm /tmp/batch.sql
}

remove_db(){
	#Removes WP user and database named $domain 
	export database_name=$(echo $domain | cut -d '.' -f1)
	#Needs mysql root password 
	read -p "Enter root mysql password: " mysql_root_password
	echo "DROP DATABASE $database_name;" >> /tmp/batch.sql
	echo "DROP USER $database_name@localhost;" >> /tmp/batch.sql
	echo "FLUSH PRIVILEGES;" >> /tmp/batch.sql
	mysql -u root -p$mysql_root_password < /tmp/batch.sql
	systemctl restart mysql
	#sudo cp /tmp/batch.sql /tmp/batch.backup
	rm /tmp/batch.sql
}

while getopts ":h:r:d:" arg; do
	case ${arg} in
		h ) 	gethelp ;;
		d ) 	export domain=$OPTARG ;
			unset remove;;
		r ) 	remove=true;
			export domain=$OPTARG;;
		\? ) gethelp;;
	esac
done

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

#Update the config
apt_update 2>&1 /dev/null

if [ $remove ]
then
	#Removes site/domain from computer
	echo "Removing $domain"
	grep -v $domain /etc/hosts > /tmp/hosts
	cp /tmp/hosts /etc/hosts
	rm /tmp/hosts
	rm -rf /var/www/$domain/
	rm /etc/apache2/sites-available/$domain.conf
	rm /etc/apache2/sites-available/$domain-ssl.conf
	rm /etc/apache2/sites-enabled/$domain.conf
	rm /etc/apache2/sites-enabled/$domain-ssl.conf
	a2dissite $domain
	certbot delete --cert-name $domain
else
	#Setup wordpress files/directory permissions
	setup_wp $domain
	#configure apache2
	config_apache
	#Prepare DB
	prepare_db
	#At this point, complete install through the web interface.
	read -p "Navigate to https://$domain to complete WP Setup (DB=$database_name).  Press enter when complete."
	#Hardening
	sudo chown root:www-data /var/www/$domain/wp-config.php
	sudo chmod 440 /var/www/$domain/wp-config.php
fi
echo "Script complete."
