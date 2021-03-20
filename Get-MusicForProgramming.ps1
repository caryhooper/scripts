#Created by Cary Hooper
#2018-06-2018
#Downloads all musicforprogramming mixes from http://www.musicforprogramming.net
#Because I was too lazy to click download 51 times

#Change This
$outputFolder = "C:\Users\Cary\Music"

#Request the main page to find all of the links
$rep = Invoke-WebRequest -URI http://www.musicforprogramming.net

#Iterate through all the links
Foreach($i in $rep.Links){

   #See if $i.InnerText matches ^[0-9][0-9] (meaning it is a link to one of the mixes)
   if($i.InnerText -match '^[0-9][0-9].*'){

       #Split GET parameter from OuterHTML
       $getparam = $i.OuterHTML.split('"')[1]
       
       $reqmix = Invoke-WebRequest -URI "http://www.musicforprogramming.net/$getparam"
       
       Foreach($j in $reqmix.Links){

           if($j.href -match '.*mp3$'){

               $filename = $j.href.split("/")[3]

               #Request all files and download to outputFolder
               Write-Host "Downloading $($filename)" #debugging
               Invoke-WebRequest $j.href -OutFile "$($outputFolder)\$($filename)"
            }
       }
    }
}
