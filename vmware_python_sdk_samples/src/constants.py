# -*- coding: utf-8 -*-

from classes import IterableConstants


class VMWARE(object):
    class STATE(IterableConstants):
        RUNNING = "poweredOn"
        STOPPED = "poweredOff"

    class OPERATIONS(IterableConstants):
        POWER_ON = "poweron"
        POWER_OFF = "poweroff"
        RESET = "reset"
        SUSPEND = "suspend"
        REBOOT = "reboot"
        SHUTDOWN = "shutdown"
        STANDBY = "standby"

    class DISKADAPTER(IterableConstants):
        """VMware supported disk adapter types"""

        SCSI = "SCSI"
        SATA = "SATA"
        IDE = "IDE"

    class NETADAPTERS(IterableConstants):
        """VMware supported network adapters"""

        E1000 = "e1000"
        E1000E = "e1000e"
        PCNET = "pcnet32"
        VMXNET = "vmxnet"
        VMXNET2 = "vmxnet2"
        VMXNET3 = "vmxnet3"

    IDE_CONTROLLER_DEVICE_KEY_BASE = 200
    MAX_IDE_DEVICES_PER_CONTROLLER = 2
    MAX_IDE_DEVICES_PER_VM = 4
    MAX_IDE_CONTROLLER = 2
    IDE_DEVICE_BASE_INDEX = 3000

    MAX_SCSI_DEVICES_PER_CONTROLLER = 16
    MAX_SCSI_DEVICES_PER_VM = 60
    MAX_SCSI_CONTROLLER = 4

    SCSI_CONTROLLER_DEVICE_KEY_BASE = 1000
    SCSI_CONTROLLER_KEY = 100
    SCSI_CONTROLLER_DEVICE_UNIT_NUMBER = 7  # pylint: disable=C0103
    SCSI_DEVICE_BASE_INDEX = 2000

    MAX_SATA_DEVICES_PER_CONTROLLER = 30
    MAX_SATA_DEVICES_PER_VM = 120
    MAX_SATA_CONTROLLER = 4

    SATA_CONTROLLER_DEVICE_KEY_BASE = 15000
    SATA_CONTROLLER_KEY = 100
    SATA_DEVICE_BASE_INDEX = 16000

    CONTROLLER_DEVICE = {
        DISKADAPTER.SCSI: {
            "controllerDeviceKeyBase": SCSI_CONTROLLER_DEVICE_KEY_BASE,
            "deviceBaseIndex": SCSI_DEVICE_BASE_INDEX,
            "maxDevicesPerController": MAX_SCSI_DEVICES_PER_CONTROLLER,
            "maxDevicesPerVm": MAX_SCSI_DEVICES_PER_VM,
            "maxController": MAX_SCSI_CONTROLLER,
            "name": DISKADAPTER.SCSI,
        },
        DISKADAPTER.IDE: {
            "controllerDeviceKeyBase": IDE_CONTROLLER_DEVICE_KEY_BASE,
            "deviceBaseIndex": IDE_DEVICE_BASE_INDEX,
            "maxDevicesPerController": MAX_IDE_DEVICES_PER_CONTROLLER,
            "maxDevicesPerVm": MAX_IDE_DEVICES_PER_VM,
            "maxController": MAX_IDE_CONTROLLER,
            "name": DISKADAPTER.IDE,
        },
        DISKADAPTER.SATA: {
            "controllerDeviceKeyBase": SATA_CONTROLLER_DEVICE_KEY_BASE,
            "deviceBaseIndex": SATA_DEVICE_BASE_INDEX,
            "maxDevicesPerController": MAX_SATA_DEVICES_PER_CONTROLLER,
            "maxDevicesPerVm": MAX_SATA_DEVICES_PER_VM,
            "maxController": MAX_SATA_CONTROLLER,
            "name": DISKADAPTER.SATA,
        },
    }

    WINDOWS_TIMEZONES = [
        {"index": "000", "name": "(GMT-12:00) International Date Line West"},
        {"index": "001", "name": "(GMT-11:00) Midway Island, Samoa"},
        {"index": "002", "name": "(GMT-10:00) Hawaii"},
        {"index": "003", "name": "(GMT-09:00) Alaska"},
        {
            "index": "004",
            "name": "(GMT-08:00) Pacific Time (US and Canada); Tijuana",
        },
        {"index": "010", "name": "(GMT-07:00) Mountain Time (US and Canada)"},
        {"index": "013", "name": "(GMT-07:00) Chihuahua, La Paz, Mazatlan"},
        {"index": "015", "name": "(GMT-07:00) Arizona"},
        {"index": "020", "name": "(GMT-06:00) Central Time (US and Canada"},
        {"index": "025", "name": "(GMT-06:00) Saskatchewan"},
        {"index": "030", "name": "(GMT-06:00) Guadalajara, Mexico City, Monterrey"},
        {"index": "033", "name": "(GMT-06:00) Central America"},
        {"index": "035", "name": "(GMT-05:00) Eastern Time (US and Canada)"},
        {"index": "040", "name": "(GMT-05:00) Indiana (East)"},
        {"index": "045", "name": "(GMT-05:00) Bogota, Lima, Quito"},
        {"index": "050", "name": "(GMT-04:00) Atlantic Time (Canada)"},
        {"index": "055", "name": "(GMT-04:00) Caracas, La Paz"},
        {"index": "056", "name": "(GMT-04:00) Santiago"},
        {"index": "060", "name": "(GMT-03:30) Newfoundland and Labrador"},
        {"index": "065", "name": "(GMT-03:00) Brasilia"},
        {"index": "070", "name": "(GMT-03:00) Buenos Aires, Georgetown"},
        {"index": "073", "name": "(GMT-03:00) Greenland"},
        {"index": "075", "name": "(GMT-02:00) Mid-Atlantic"},
        {"index": "080", "name": "(GMT-01:00) Azores"},
        {"index": "083", "name": "(GMT-01:00) Cape Verde Islands"},
        {
            "index": "085",
            "name": "(GMT) Greenwich Mean Time: Dublin, Edinburgh, Lisbon, London",
        },
        {"index": "090", "name": "(GMT) Casablanca, Monrovia"},
        {
            "index": "095",
            "name": "(GMT+01:00) Belgrade, Bratislava, Budapest, Ljubljana, Prague",
        },
        {"index": "100", "name": "(GMT+01:00) Sarajevo, Skopje, Warsaw, Zagreb"},
        {"index": "105", "name": "(GMT+01:00) Brussels, Copenhagen, Madrid, Paris"},
        {
            "index": "110",
            "name": "(GMT+01:00) Amsterdam, Berlin, Bern, Rome, Stockholm, Vienna",
        },
        {"index": "113", "name": "(GMT+01:00) West Central Africa"},
        {"index": "115", "name": "(GMT+02:00) Bucharest"},
        {"index": "120", "name": "(GMT+02:00) Cairo"},
        {
            "index": "125",
            "name": "(GMT+02:00) Helsinki, Kiev, Riga, Sofia, Tallinn, Vilnius",
        },
        {"index": "130", "name": "(GMT+02:00) Athens, Istanbul, Minsk"},
        {"index": "135", "name": "(GMT+02:00) Jerusalem"},
        {"index": "140", "name": "(GMT+02:00) Harare, Pretoria"},
        {"index": "145", "name": "(GMT+03:00) Moscow, St. Petersburg, Volgograd"},
        {"index": "150", "name": "(GMT+03:00) Kuwait, Riyadh"},
        {"index": "155", "name": "(GMT+03:00) Nairobi"},
        {"index": "158", "name": "(GMT+03:00) Baghdad"},
        {"index": "160", "name": "(GMT+03:30) Tehran"},
        {"index": "165", "name": "(GMT+04:00) Abu Dhabi, Muscat"},
        {"index": "170", "name": "(GMT+04:00) Baku, Tbilisi, Yerevan"},
        {"index": "175", "name": "(GMT+04:30) Kabul"},
        {"index": "180", "name": "(GMT+05:00) Ekaterinburg"},
        {"index": "185", "name": "(GMT+05:00) Islamabad, Karachi, Tashkent"},
        {"index": "190", "name": "(GMT+05:30) Chennai, Kolkata, Mumbai, New Delhi"},
        {"index": "193", "name": "(GMT+05:45) Kathmand"},
        {"index": "195", "name": "(GMT+06:00) Astana, Dhaka"},
        {"index": "200", "name": "(GMT+06:00) Sri Jayawardenepura"},
        {"index": "201", "name": "(GMT+06:00) Almaty, Novosibirsk"},
        {"index": "203", "name": "(GMT+06:30) Yangon Rangoon"},
        {"index": "205", "name": "(GMT+07:00) Bangkok, Hanoi, Jakarta"},
        {"index": "207", "name": "(GMT+07:00) Krasnoyarsk"},
        {
            "index": "210",
            "name": "(GMT+08:00) Beijing, Chongqing, Hong Kong SAR, Urumqi",
        },
        {"index": "215", "name": "(GMT+08:00) Kuala Lumpur, Singapore"},
        {"index": "220", "name": "(GMT+08:00) Taipei"},
        {"index": "225", "name": "(GMT+08:00) Perth"},
        {"index": "227", "name": "(GMT+08:00) Irkutsk, Ulaanbaatar"},
        {"index": "230", "name": "(GMT+09:00) Seoul"},
        {"index": "235", "name": "(GMT+09:00) Osaka, Sapporo, Tokyo"},
        {"index": "240", "name": "(GMT+09:00) Yakutsk"},
        {"index": "245", "name": "(GMT+09:30) Darwin"},
        {"index": "250", "name": "(GMT+09:30) Adelaide"},
        {"index": "255", "name": "(GMT+10:00) Canberra, Melbourne, Sydney"},
        {"index": "260", "name": "(GMT+10:00) Brisbane"},
        {"index": "265", "name": "(GMT+10:00) Hobart"},
        {"index": "270", "name": "(GMT+10:00) Vladivostok"},
        {"index": "275", "name": "(GMT+10:00) Guam, Port Moresby"},
        {
            "index": "280",
            "name": "(GMT+11:00) Magadan, Solomon Islands, New Caledonia",
        },
        {
            "index": "285",
            "name": "(GMT+12:00) Fiji Islands, Kamchatka, Marshall Islands",
        },
        {"index": "290", "name": "(GMT+12:00) Auckland, Wellington"},
        {"index": "300", "name": "(GMT+13:00) Nuku'alofa"},
    ]
