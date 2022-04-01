import os, sys
sys.path.append(os.path.dirname(os.path.realpath(__file__)))


def main(weasel):
   
    weasel.menu_file()
    weasel.menu_view()
    weasel.menu_edit()

    #menu = weasel.menu('iBEAt pilot')

    menu = weasel.menu(label = "iBEAt dev")

    menu.item(
        label = 'XNAT iBEAt Download',
        functionName = 'download',
        pipeline = 'XNAT__App_iBEAt')
    menu.item(
        label = 'Rename DICOMs (Siemens) iBEAt',
        pipeline = 'iBEAt_Siemens_Rename_Data_Leeds_Button')

    menu.separator()

    menu.item(
        label = 'T2* MDR (Siemens)',
        pipeline = 'MDR_iBEAt_T2Star_Button')
    menu.item(
        label = 'T2 MDR (Siemens)',
        pipeline = 'MDR_iBEAt_T2_Button')
    menu.item(
        label = 'T1 MDR (Siemens)',
        pipeline = 'MDR_iBEAt_T1_Button')
    menu.item(
        label = 'IVIM MDR (Siemens)',
        pipeline = 'MDR_iBEAt_DWI_Button')
    menu.item(
        label = 'DTI MDR (Siemens)',
        pipeline = 'MDR_iBEAt_DTI_Button')
    #menu.item(
    #    label = 'DCE MDR (Siemens)',
    #    pipeline = 'MDR_iBEAt_DCE_Button')
    menu.item(
        label = 'MT MDR (Siemens)',
        pipeline = 'MDR_iBEAt_MT_Button')

    menu.separator()

    menu.item(
        label = 'MDR ALL SERIES (Siemens) iBEAt',
        pipeline = 'MDR_allSeries_iBEAt_Button')

    menu.item(
        label = 'MDR ALL SERIES (Siemens) iBEAt (No Import from XNAT)',
        pipeline = 'MDR_allSeries_iBEAt_Button_NO_importing')
        
    menu.separator()

    menu.item(
        label = 'Joint T1 & T2 Mapping (Siemens)',
        pipeline = 'iBEAt_SiemensT1T2MapButton')
    menu.item(
        label = 'T2* Mapping (Siemens)',
        pipeline = 'iBEAt_SiemensT2sMapButton')
    menu.item(
        label = 'IVIM: ADC Mapping (Siemens)',
        pipeline = 'iBEAt_SiemensIVIMButton')
    menu.item(
        label = 'DTI: FA Mapping (Siemens)',
        pipeline = 'iBEAt_SiemensDTIButton')

    menu.separator()

    menu.item(
        label = 'XNAT iBEAt Upload',
        functionName = 'upload',
        pipeline = 'XNAT__App_iBEAt')


        

        
