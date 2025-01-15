#Requires AutoHotkey v2.0
Persistent

; Set up the timer
SetTimer(AutoSave, 300000)  ; 300000 ms = 5 minutes (adjust as needed)

AutoSave() {
    Send("^s")  ; Send Ctrl+S to save
}

; F12 hotkey to toggle autosave
F12::
{
    static isEnabled := true
    if (isEnabled)
    {
        SetTimer(AutoSave, 0)  ; Disable timer
        MsgBox("Autosave disabled")
        isEnabled := false
    }
    else
    {
        SetTimer(AutoSave, 300000)  ; Re-enable timer
        MsgBox("Autosave enabled (every 5 minutes)")
        isEnabled := true
    }
}
