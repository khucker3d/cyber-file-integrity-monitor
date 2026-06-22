# How To: File Integrity Monitor (V1)

## Prep:
1. Download the Python [script](https://github.com/khucker3d/cyber-file-integrity-monitor/blob/main/file_integrity_monitor.py)
2. Verify/Install required dependencies via CLI: ```pip install watchdog```
<img width="566" height="257" alt="Dependencies" src="https://github.com/user-attachments/assets/935c2f73-c11f-446a-bfff-bc4c22bc97e2" />


### Create Folder & Add Files:
1. Create a new folder called **"watched"**
2. Add the file(s) that will be monitored
<img width="496" height="139" alt="1_SetupWatchFolderAndAddFile" src="https://github.com/user-attachments/assets/95110f79-2880-49ff-8d57-e67439876993" />


## Using the Tool:
3. Open the script using the CLI command: 
   * Power Shell:```python file_integrity_monitor.py```
   * Terminal:```python3 file_integrity_monitor.py```

### Set Path:
4. Select the Browse button and point to the **"watched"** folder's location 
<img width="899" height="120" alt="Path" src="https://github.com/user-attachments/assets/fe2ae21d-c0ee-4a80-8937-3c0e81149ab5" />


### Create the Baseline JSON
5. Ensure data files are finalized and approved
6. Click **Create Baseline** and verify by reviewing the output
<img width="441" height="19" alt="4_BaselineCreated" src="https://github.com/user-attachments/assets/6c269871-8665-42c3-8cfb-cdaee330aaa4" />


### Start Monitoring
7. Click **Start Monitoring**
<img width="899" height="409" alt="5_StartMonitering" src="https://github.com/user-attachments/assets/bc5fd41f-a0bb-4f17-8b57-ae299130d05f" />

8. In the Output, look for the tool scanning messages to verify
<img width="672" height="42" alt="Screenshot 2026-06-21 at 20 55 19" src="https://github.com/user-attachments/assets/6d96ebd0-3f60-4114-9c90-638c8a4cb292" />

### Discovery & Escalation
9. When the file data has been changed:

   * File change will be indicated in the Dashboard Counters
     <img width="355" height="43" alt="Screenshot 2026-06-21 at 20 15 45" src="https://github.com/user-attachments/assets/7f5e78c0-69c6-4322-ad9a-b02eaec8a150" />
    
   * The changes will appear in red text
     <img width="757" height="609" alt="6_ChangesAlert" src="https://github.com/user-attachments/assets/b65cffdb-1fec-4826-b7a0-3089d647cb6a" />

10. Submit a **Review Note** *(Optional)* to note in the Output that you observed the alert and escalating following protocol standards 
  
11. Once the solution is found and approved, choose the instructed response Action:

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
