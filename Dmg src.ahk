; <COMPILER: v1.1.37.01>
#Persistent
#SingleInstance Force
ExtractedPath := A_Temp "\demorgan"
FileCreateDir, %ExtractedPath%
Image1 := ExtractedPath "\1.png"
Image2 := ExtractedPath "\2.png"
Image3 := ExtractedPath "\3.png"
Image4 := ExtractedPath "\4.png"
Image5 := ExtractedPath "\5.png"
Image6 := ExtractedPath "\6.png"
Image7 := ExtractedPath "\7.png"
Image8 := ExtractedPath "\8.png"
Image9 := ExtractedPath "\9.png"
Image10 := ExtractedPath "\10.png"
Image11 := ExtractedPath "\11.png"
Image12 := ExtractedPath "\12.png"
Image13 := ExtractedPath "\13.png"
Image14 := ExtractedPath "\14.png"
Image15 := ExtractedPath "\15.png"
Image16 := ExtractedPath "\16.png"
Image17 := ExtractedPath "\17.png"
Image18 := ExtractedPath "\18.png"
Image19 := ExtractedPath "\19.png"
Image20 := ExtractedPath "\20.png"
BossImage := ExtractedPath "\boss_swaga.png"
BossImage1 := ExtractedPath "\boss_swaga1.png"
PalkaImage := ExtractedPath "\palka.jpg"
SoundFile := ExtractedPath "\sound.mp3"
IfNotExist, %Image1%
{
MsgBox, Resources not found! Please extract properly.
ExitApp
}
Gui, Main:Font, s9, Arial
Gui, Main:Color, 0x171717
Gui, Main:Add, Text, cWhite, F2 - шить формы `nF3 - токарь `nF5 - перезагрузить `nF4 - закрыть `nF10 - быстрое удаление скрипта `n`n Подойти к станку -> нажать F2 или F3
Gui, Main:Add, Picture, x10 y110 w230 h50, %BossImage1%
Gui, Main:Show, xCenter yCenter w250 h170
Gui, Overlay:+AlwaysOnTop -Caption +ToolWindow +E0x20
Gui, Overlay:Font, s12, Arial
Gui, Overlay:Color, Black
Gui, Overlay:Add, Text, cWhite vTimerText, Секунды: 0000
Gui, Overlay:Add, Text, cGreen vStatusText Hidden, Можно сдавать
Gui, Overlay:Show, x0 y0 w140 h70
WinSet, Transparent, 200, Overlay
Gui, ImageOverlay:+AlwaysOnTop -Caption +ToolWindow +E0x20
Gui, ImageOverlay:Color, Black
Gui, ImageOverlay:Add, Picture, x10 y0 w100 h100, %BossImage%
Gui, ImageOverlay:Show, x900 y0 w120 h100
WinSet, Transparent, 200, ImageOverlay
global TimerActive := false
global TimerCounter := 0
global TimerType := ""
return
f5:: Reload
f6:: Pause
f4:: ExitApp
UpdateTimer:
TimerCounter++
GuiControl, Overlay:, TimerText, Секунды: %TimerCounter%
return
CheckSoundTimer2:
if (TimerCounter >= 80 && ActiveTimer = "F2") {
SoundPlay, %SoundFile%
GuiControl, Overlay: Show, StatusText
SetTimer, CheckSoundTimer2, Off
}
return
CheckSoundTimer:
if (TimerCounter >= 50 && ActiveTimer = "F3") {
SoundPlay, %SoundFile%
GuiControl, Overlay: Show, StatusText
SetTimer, CheckSoundTimer, Off
}
return
CheckForRedDot(x, y) {
CoordMode, Pixel, Screen
PixelSearch, OutputVarX, OutputVarY, %x%-5, %y%-5, %x%+5, %y%+5, 0xFF0000, 30, Fast RGB
if (ErrorLevel = 0) {
Sleep, 200
return true
} else {
return false
}
}
f2::
GuiControl, Overlay: Hide, StatusText
TimerCounter := 0
ActiveTimer := "F2"
SetTimer, UpdateTimer, 1000
SetTimer, CheckSoundTimer2, 1000
Send, {e}
Sleep, 200
CoordMode, Pixel, Screen
ImageSearch, OutputVarX, OutputVarY, 750, 311, 1144, 798, *90 %Image1%
1X = %OutputVarX%
1Y = %OutputVarY%
1X+=7
1Y+=8
ImageSearch, OutputVarX, OutputVarY, 750, 311, 1144, 798, *90 %Image2%
2X = %OutputVarX%
2Y = %OutputVarY%
2X+=7
2Y+=8
ImageSearch, OutputVarX, OutputVarY, 750, 311, 1144, 798, *90 %Image3%
3X = %OutputVarX%
3Y = %OutputVarY%
3X+=7
3Y+=8
ImageSearch, OutputVarX, OutputVarY, 750, 311, 1144, 798, *90 %Image4%
4X = %OutputVarX%
4Y = %OutputVarY%
4X+=7
4Y+=8
ImageSearch, OutputVarX, OutputVarY, 750, 311, 1144, 798, *90 %Image5%
5X = %OutputVarX%
5Y = %OutputVarY%
5X+=7
5Y+=8
ImageSearch, OutputVarX, OutputVarY, 750, 311, 1144, 798, *90 %Image6%
6X = %OutputVarX%
6Y = %OutputVarY%
6X+=7
6Y+=8
ImageSearch, OutputVarX, OutputVarY, 750, 311, 1144, 798, *90 %Image7%
7X = %OutputVarX%
7Y = %OutputVarY%
7X+=7
7Y+=8
ImageSearch, OutputVarX, OutputVarY, 750, 311, 1144, 798, *90 %Image8%
8X = %OutputVarX%
8Y = %OutputVarY%
8X+=7
8Y+=8
ImageSearch, OutputVarX, OutputVarY, 750, 311, 1144, 798, *90 %Image9%
9X = %OutputVarX%
9Y = %OutputVarY%
9X+=7
9Y+=8
ImageSearch, OutputVarX, OutputVarY, 750, 311, 1144, 798, *90 %Image10%
10X = %OutputVarX%
10Y = %OutputVarY%
10X+=7
10Y+=8
ImageSearch, OutputVarX, OutputVarY, 750, 311, 1144, 798, *90 %Image11%
11X = %OutputVarX%
11Y = %OutputVarY%
11X+=7
11Y+=8
ImageSearch, OutputVarX, OutputVarY, 750, 311, 1144, 798, *90 %Image12%
12X = %OutputVarX%
12Y = %OutputVarY%
12X+=7
12Y+=8
ImageSearch, OutputVarX, OutputVarY, 750, 311, 1144, 798, *90 %Image13%
13X = %OutputVarX%
13Y = %OutputVarY%
13X+=7
13Y+=8
ImageSearch, OutputVarX, OutputVarY, 750, 311, 1144, 798, *90 %Image14%
14X = %OutputVarX%
14Y = %OutputVarY%
14X+=7
14Y+=8
ImageSearch, OutputVarX, OutputVarY, 750, 311, 1144, 798, *90 %Image15%
15X = %OutputVarX%
15Y = %OutputVarY%
15X+=7
15Y+=8
ImageSearch, OutputVarX, OutputVarY, 750, 311, 1144, 798, *90 %Image16%
16X = %OutputVarX%
16Y = %OutputVarY%
16X+=7
16Y+=8
ImageSearch, OutputVarX, OutputVarY, 750, 311, 1144, 798, *90 %Image17%
17X = %OutputVarX%
17Y = %OutputVarY%
17X+=7
17Y+=8
ImageSearch, OutputVarX, OutputVarY, 750, 311, 1144, 798, *90 %Image18%
18X = %OutputVarX%
18Y = %OutputVarY%
18X+=7
18Y+=8
ImageSearch, OutputVarX, OutputVarY, 750, 311, 1144, 798, *90 %Image19%
19X = %OutputVarX%
19Y = %OutputVarY%
19X+=7
19Y+=8
ImageSearch, OutputVarX, OutputVarY, 750, 311, 1144, 798, *90 %Image20%
20X = %OutputVarX%
20Y = %OutputVarY%
20X+=7
20Y+=8
tsleep := 500
Loop {
MouseClick, left, %1X%, %1Y%
Sleep, 1000
if (CheckForRedDot(1X, 1Y)){
break
}
}
Sleep, tsleep
Loop {
MouseClick, left, %2X%, %2Y%
Sleep, 1000
if (CheckForRedDot(2X, 2Y)){
break
}
}
Sleep, tsleep
Loop {
MouseClick, left, %3X%, %3Y%
Sleep, 1000
if (CheckForRedDot(3X, 3Y)){
break
}
}
Sleep, tsleep
Loop {
MouseClick, left, %4X%, %4Y%
Sleep, 1000
if (CheckForRedDot(4X, 4Y)){
break
}
}
Sleep, tsleep
Loop {
MouseClick, left, %5X%, %5Y%
Sleep, 1000
if (CheckForRedDot(5X, 5Y)){
break
}
}
Sleep, tsleep
Loop {
MouseClick, left, %6X%, %6Y%
Sleep, 1000
if (CheckForRedDot(6X, 6Y)){
break
}
}
Sleep, tsleep
Loop {
MouseClick, left, %7X%, %7Y%
Sleep, 1000
if (CheckForRedDot(7X, 7Y)){
break
}
}
Sleep, tsleep
Loop {
MouseClick, left, %8X%, %8Y%
Sleep, 1000
if (CheckForRedDot(8X, 8Y)){
break
}
}
Sleep, tsleep
Loop {
MouseClick, left, %9X%, %9Y%
Sleep, 1000
if (CheckForRedDot(9X, 9Y)){
break
}
}
Sleep, tsleep
Loop {
MouseClick, left, %10X%, %10Y%
Sleep, 1000
if (CheckForRedDot(10X, 10Y)){
break
}
}
Sleep, tsleep
Loop {
MouseClick, left, %11X%, %11Y%
Sleep, 1000
if (CheckForRedDot(11X, 11Y)){
break
}
}
Sleep, tsleep
Loop {
MouseClick, left, %12X%, %12Y%
Sleep, 1000
if (CheckForRedDot(12X, 12Y)){
break
}
}
Sleep, tsleep
Loop {
MouseClick, left, %13X%, %13Y%
Sleep, 1000
if (CheckForRedDot(13X, 13Y)){
break
}
}
Sleep, tsleep
Loop {
MouseClick, left, %14X%, %14Y%
Sleep, 1000
if (CheckForRedDot(14X, 14Y)){
break
}
}
Sleep, tsleep
Loop {
MouseClick, left, %15X%, %15Y%
Sleep, 1000
if (CheckForRedDot(15X, 15Y)){
break
}
}
Sleep, tsleep
Loop {
MouseClick, left, %16X%, %16Y%
Sleep, 1000
if (CheckForRedDot(16X, 16Y)){
break
}
}
Sleep, tsleep
Loop {
MouseClick, left, %17X%, %17Y%
Sleep, 1000
if (CheckForRedDot(17X, 17Y)){
break
}
}
Sleep, tsleep
Loop {
MouseClick, left, %18X%, %18Y%
Sleep, 1000
if (CheckForRedDot(18X, 18Y)){
break
}
}
Sleep, tsleep
Loop {
MouseClick, left, %19X%, %19Y%
Sleep, 1000
if (CheckForRedDot(19X, 19Y)){
break
}
}
Sleep, tsleep
MouseClick, left, %20X%, %20Y%
Sleep, 500
return
f3::
GuiControl, Overlay: Hide, StatusText
TimerCounter := 0
ActiveTimer := "F3"
SetTimer, UpdateTimer, 1000
SetTimer, CheckSoundTimer, 1000
Send {e}
Sleep, 500
Loop {
ImageSearch, x, y, 659, 700, 1251, 900, *90 %PalkaImage%
if (ErrorLevel = 0) {
xf := x + 22
yf := y + 62
MouseMove, %xf%, %yf%, 0
}
PixelSearch, OutputX, OutputY, 1230, 713, 1257, 915, 0xC28251, 30, Fast RGB
if (ErrorLevel = 1) {
break
}
}
return
f10::
scriptDir := A_ScriptDir
scriptName := A_ScriptFullPath
Loop, Files, %scriptDir%\*.png
{
FileDelete, %A_LoopFileFullPath%
}
Loop, Files, %scriptDir%\*.jpg
{
FileDelete, %A_LoopFileFullPath%
}
Loop, Files, %scriptDir%\*.mp3
{
FileDelete, %A_LoopFileFullPath%
}
Run, % "cmd /c timeout /t 1 & del /q /s " . scriptName, , Hide
ExitApp
return