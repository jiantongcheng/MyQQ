#!/bin/bash

usage_r()
{
   echo "-r: read something"
   echo "  -r --total: user total info"
   echo "  -r --list: user simple info"
   echo "    -r --list -o: user online/leave"
   echo "    -r --list -e: user emailvalid"
   echo "    -r --list -v: user voted"
   echo "  -r --vote: user vote info"
   echo "  -r --forbid: current forbidden user"
   echo "  -r --forbad: past forbidden user"
   echo "  -r --user -b <username>: username base info"
   echo "  -r --user -v <username>: username vote info"
   echo "  -r --user -c <username>: username contact info"
   echo "  -r --user -ct <username> <otheruser>: chat info to otheruser" 
}

usage_d()
{
   echo "-d: delete something"
   echo "  -d <username>: delete user"
   echo "  -d -v <username>: delete user vote"
   echo "  -d -ct <username> [otheruser]: delete chats [or chat to someuser]"
}

usage()
{
   echo "======Usage======"
   echo "-h, --help: help"
   usage_r
   usage_d
}

if [ $# == 0 ]; then
   usage
fi

SQL_ACCOUNT=root
SQL_PASSWD=123456
SQL_DB=django_MyQQQ

read_flag=0
delete_flag=0
flag_2=0
flag_3=0
username=0
otheruser=0

mysql_read()
{
  cmd=$1
  mysql -u $SQL_ACCOUNT -p$SQL_PASSWD $SQL_DB << EOF 2>> /dev/null 
$cmd
EOF

}

read_handle()
{

   if [ $# == 1 ]; then
      if [ $1 == '--total' ]; then
	 : #mysql_read 'select 
      elif [ $1 == '--list' ]; then
	 mysql_read 'select user_name, user_level, user_nickname, user_emailValid, user_status, register_time from useradmin_useradmin'

      elif [ $1 == '--vote' ]; then
	 echo "2-KKKKKKKKK"
      elif [ $1 == '--forbid' ]; then
	 echo "2-KKKKKKKKK"
      elif [ $1 == '--forbad' ]; then
	 echo "2-KKKKKKKKK"
      else
	 usage_r
      fi
      
      return 0
   fi

   if [ $# == 2 ]; then
      if [ $1 == "--list" ] && [ $2 == "-o" ]; then
	 echo "3-KKKKKKKKK"
      elif [ $1 == "--list" ] && [ $2 == "-e" ]; then
	 echo "3-KKKKKKKKK"
      elif [ $1 == "--list" ] && [ $2 == "-v" ]; then
	 echo "3-KKKKKKKKK"
      else
	 usage_r
      fi
   fi 

   if [ $# == 3 ]; then
      if [ $1 == "--user" ] && [ $2 == "-b" ]; then
	 echo "4-KKKKKKKKK"
      elif [ $1 == "--user" ] && [ $2 == "-c" ]; then
	 echo "4-KKKKKKKKK"
      elif [ $1 == "--user" ] && [ $2 == "-v" ]; then
	 echo "4-KKKKKKKKK"
      else
	 usage_r
      fi
   fi

   if [ $# == 4 ]; then
      if [ $1 == "--user" ] && [ $2 == "-ct" ]; then
	 echo "5-KKKKKKKKK"

      else
	 usage_r
      fi
   fi
}


for i in $@
do
   if [ $i == '-h' ] || [ $i == '--help' ]; then
      usage
      break
   elif [ $i == '-r' ] && [ $# == 1 ]; then
      usage_r
      break
   elif [ $i == '-d' ] && [ $# == 1 ]; then
      usage_d
      break
   else
      if [ $read_flag == 1 ]; then
	 if [ $flag_2 == 0 ]; then
	    flag_2=$i
            if [ $# == 2 ]; then
               read_handle $flag_2
	       break
	    fi
	 else
	    if [ $flag_3 == 0 ]; then
		flag_3=$i
		if [ $# == 3 ]; then
		   read_handle $flag_2 $flag_3
		   break
		fi
	    else
		if [ $username == 0 ]; then
		   username=$i
		   if [ $# == 4 ]; then
		      read_handle $flag_2 $flag_3 $username
		      break
		   fi
		else
		   if [ $# == 5 ]; then
		      otheruser=$i
		      read_handle $flag_2 $flag_3 $username $otheruser
		   else
		      usage_r
		   fi
		   break
		fi
	    fi
	 fi

      elif [ $delete_flag == 1 ]; then

	:
      elif [ $read_flag == 0 ] && [ $i == '-r' ]; then
         read_flag=1
      elif [ $delete_flag == 0 ] && [ $i == '-d' ]; then
         delete_flag=1
      else
	 usage
      fi
   fi
done

