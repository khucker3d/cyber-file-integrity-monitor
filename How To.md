# How To: File Integrity Monitor 
_Doc is WIP_

## Requirements
1. Download the Python [script](https://github.com/khucker3d/cyber-file-integrity-monitor/blob/main/file_integrity_monitor.py)
2. Verify/Install dependencies:
   * ```pip install watchdog```
   * ```pip install tkinter```  
      _**Note:** On some Linux distributions, Tkinter may need to be installed separately:_ ```sudo apt install python3-tk```
3. Ensure the data file is updated and approved before using the tool


***Admin/root Notes:***
- *Normal user permissions are usually enough for monitoring files inside your own project folder.*
- *Admin/root permissions may be required if monitoring protected system directories.*
- *Do not run as admin/root unless the monitored path requires it.*


## Add Files:
1. Create a new folder called **"watched"** in the location best suited
2. Add the file(s) that will be monitored to the **"watched"** folder

   <img width="500" height="273" alt="1_SetupWatchFolderAndAddFile" src="https://github.com/user-attachments/assets/eb0e7173-4a83-40ea-928c-4fbfb9437c6f" />

## Run the tool:
   * Windows Power Shell:```python file_integrity_monitor.py```
   * Mac/Linux Terminal:```python3 file_integrity_monitor.py```

## Create the Baseline JSON
1. Click **Create Baseline** and verify by reviewing the output.

   <img width="441" height="35" alt="4_BaselineCreated" src="https://github.com/user-attachments/assets/f1333378-f22a-467b-af45-878c80336992" />

## Monitering
1. Click **Start Monitoring**.

   <img width="899" height="409" alt="5_StartMonitering" src="https://github.com/user-attachments/assets/1e7d4e82-a934-43e0-9df0-3e9bd1e06ebc" />

## Discovery & Escalation
1. When the tool reports a modification, the changes will appear in red text.

   <img width="757" height="609" alt="6_ChangesAlert" src="https://github.com/user-attachments/assets/74b41449-76f2-41cb-ab1b-cee4e711679f" />

2. Review the event log and proceed with the appropriate escalation protocol

   <img width="898" height="119" alt="7_ActionsOptions" src="https://github.com/user-attachments/assets/9366c351-0114-4c05-ba0f-fd65ba42495c" />
  
3. Once the action is approved, choose the instructed response Action:

   
   
   <img width="528" height="208" alt="8_Opt1_1Revert_All_Change" src="https://github.com/user-attachments/assets/c5cc1592-40ff-4382-99ea-419ad62ad280" />
     
     _Once reverted, an output message will appear_
      
     <img width="819" height="49" alt="8_Opt1_2Revert_All_Change_ResultOutput" src="https://github.com/user-attachments/assets/4dd6ce3c-adac-498b-9284-13465fade3b7" />

## Action Types:
### Overwrite Data:** Best for individual changes
   
  _1. Enter the Field Label_
     
  <img width="685" height="405" alt="8_Opt2_2Overwrite_Specific_Data_LDAP" src="https://github.com/user-attachments/assets/443e9944-9775-4c12-8a36-bdcb7b88ddbb" />

   _2. Enter the Field Label_
   
   <img width="276" height="298" alt="8_Opt2_4Overwrite_Specific_Data_LDAP" src="https://github.com/user-attachments/assets/c7b622d3-b482-4a57-b93f-e42ce7500b6b" />

   _3. Enter the label change_
   
   <img width="592" height="198" alt="8_Opt2_3Overwrite_Specific_Data_LDAP" src="https://github.com/user-attachments/assets/8f763f32-a18b-4c6d-9889-5372c950dea8" />

### Add Review Note _(Output Console)_:** This should be applied for any Actions take
     
  <img width="292" height="171" alt="LogNote" src="https://github.com/user-attachments/assets/ee3002b9-e493-4100-8220-118f3145a2ce" />

   _Once accepted, an output message will appear_
    <img width="816" height="25" alt="LogNoteOutput" src="https://github.com/user-attachments/assets/d36729c7-fbce-43eb-a46d-f8ffcf148200" />
