#Created by Cary Hooper
#2018-06-2018
#Downloads all musicforprogramming mixes from http://www.musicforprogramming.net
#Because I was too lazy to click download 51 times
#Updated 2022-02-05. Noticed site had major update including .mp3 links in JavaScript. This carves out the .mp3 links from the JavaScript and downloads from the hosting CDN.

#Change This
$outputFolder = "C:\Users\carye\Music"

#Request the main page to find all of the links
$rep = Invoke-WebRequest -URI http://www.musicforprogramming.net/latest

#Iterate through all the links
Foreach($i in $rep.Links){


   #See if $i.InnerText matches ^[0-9][0-9] (meaning it is a link to one of the mixes)
   if($i.InnerText -match '^[0-9][0-9].*'){
       #Split GET parameter from OuterHTML
       $getparam = $i.OuterHTML.split('"')[1]
       Write-Host "Requesting /$getparam"
       
       
       $reqmix = Invoke-WebRequest -URI "http://www.musicforprogramming.net/$getparam/"
       
       Foreach($j in $reqmix.ParsedHtml.all.tags("script")){
           #Iterate through all 'script' tags to find the link.  There is definitely an easier way to do this
           #in Powershell (there has to be!).  Long live python's bs4.
           if($j.Text -match '.*\.mp3.*'){
               #Only match script tags with mp3 inside of them.

               #Pull out the URL from the (json?) snippet __SAPPER__
               $tempstring = $j.Text
               $urlindex = $tempstring.IndexOf('file:"') + 6
               $endindex = $tempstring.IndexOf('.mp3') + 4
               #Good old JS-style string slicing!
               $url_encoded = $tempstring.substring($urlindex, $endindex - $urlindex)
               #Unicode decode the '/' characters
               $url = $url_encoded -Replace '\\u002F','/'
               
               $filename = $url.split("/")[3]

               #Request all files and download to outputFolder
               Write-Host "Downloading $($url)" #debugging
               Invoke-WebRequest $url -OutFile "$($outputFolder)\$($filename)"
           
            }
       }
    }
}
