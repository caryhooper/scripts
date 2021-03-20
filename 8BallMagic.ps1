#Magic 8-Ball Script
#Cary Hooper and Ricky Brown

While($true) {
#Ask the question
$question = Read-Host -Prompt "Input your question."
#Get Random Number 
$rand = Get-Random -Minimum 0 -Maximum 19
#Place all 20 answers into an array
$answersString = "It is certain,It is decidedly so,Without a doubt,Yes definitely,You may rely on it,As I see it, yes,Most likely,Outlook good,Yes,Signs point to yes,Reply hazy try again,Ask again later,Better not tell you now,Cannot predict now,Concentrate and ask again,Don't count on it,My reply is no,My sources say no,Outlook not so good,Very doubtful"
$answersArray = $answersString.split(",")
#Give Random Answer
Write-Host $answersArray[$rand] "`n"
}