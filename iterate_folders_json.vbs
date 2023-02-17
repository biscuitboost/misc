' Set the target directory to traverse
strTargetDir = "C:\Example\Directory"

' Create the JSON object to output to
Set objJSON = CreateObject("Scripting.Dictionary")
Set objRecords = CreateObject("Scripting.Dictionary")
objJSON("collectionName") = "My Collection Name"
objJSON("recordCount") = 0
objJSON("records") = objRecords

' Call the recursive function to traverse the directory
TraverseDirectory strTargetDir, objRecords

' Output the JSON object
WScript.Echo JsonConverter.ConvertToJson(objJSON, True)

' Recursive function to traverse the directory and output file information
Sub TraverseDirectory(strDirPath, objRecords)
    ' Get a reference to the current directory object
    Set objDir = CreateObject("Scripting.FileSystemObject").GetFolder(strDirPath)
    
    ' Loop through all the files in the current directory
    For Each objFile In objDir.Files
        ' Separate the directory name into two fields based on the pattern
        arrDir = Split(objDir.Name, "(")
        strDir1 = arrDir(0)
        strDir2 = Replace(arrDir(1), ")", "")
        
        ' Get the file size in bytes
        lngFileSize = objFile.Size
        
        ' Get the MIME content type of the file
        strContentType = GetContentType(objFile.Path)
        
        ' Create a new record for the file
        Set objAttributes = CreateObject("Scripting.Dictionary")
        objAttributes("Directory 1") = Array(strDir1)
        objAttributes("Directory 2") = Array(strDir2)
        objAttributes("Filename") = Array(objFile.Name)
        Set objContent = CreateObject("Scripting.Dictionary")
        Set objContentInfo = CreateObject("Scripting.Dictionary")
        objContentInfo("contentType") = strContentType
        objContentInfo("filename") = "/DMS_staging/example/inbound/" & objFile.Name
        objContentInfo("length") = lngFileSize
        objContentInfo("offset") = 0
        objContent(objFile.Name) = objContentInfo
        Set objRecord = CreateObject("Scripting.Dictionary")
        objRecord("attributes") = objAttributes
        objRecord("content") = objContent
        
        ' Add the record to the JSON object
        objRecords.Add objFile.Path, objRecord
        objJSON("recordCount") = objJSON("recordCount") + 1
    Next
    
    ' Recursively call this function on all the subdirectories of the current directory
    For Each objSubDir In objDir.SubFolders
        Set objSubRecords = CreateObject("Scripting.Dictionary")
        objRecords.Add objSubDir.Path, objSubRecords
        TraverseDirectory objSubDir.Path, objSubRecords
    Next
End Sub

' Function to get the MIME content type of a file
Function GetContentType(strFilePath)
    ' Create a new ADODB.Stream object
    Set objStream = CreateObject("ADODB.Stream")
    
    ' Set the type of the stream to binary
    objStream.Type = 1
    
    ' Open the file and load its contents into the stream object
    objStream.Open
    objStream.LoadFromFile strFilePath
    
    ' Get the MIME content type of the file from the stream object
    strContentType = objStream.TypeInfo
    
    ' Clean up and return the content type
    objStream.Close
    Set objStream = Nothing
    GetContentType = strContentType
End Function
