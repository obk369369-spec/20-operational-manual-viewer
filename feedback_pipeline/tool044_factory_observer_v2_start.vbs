Option Explicit
Dim shell, fso, base, py, cmd
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
base = fso.GetParentFolderName(WScript.ScriptFullName)
py = shell.ExpandEnvironmentStrings("%USERPROFILE%") & "\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
If Not fso.FileExists(py) Then
  MsgBox "검증된 Python 실행환경을 찾지 못했습니다.", 48, "TOOL044 V2"
  WScript.Quit 2
End If
cmd = Chr(34) & py & Chr(34) & " " & Chr(34) & base & "\tool044_factory_observer_v2.py" & Chr(34) & " --root " & Chr(34) & base & Chr(34)
shell.Run cmd, 0, False
WScript.Sleep 1200
shell.Run "http://127.0.0.1:8044/tool044_factory_observer_v2.html", 1, False
