"""
Initialize Workspace, WorkingDirectory and Channel of Analysis
"""
import Main_Class

class _init_Workspace:
    def initWorkspace(self, path='/home/cellfinder_data', channel=0, choice="Hemisphere"):
        if channel == 0:
            channelStr = "C01"
        elif channel == 1:
            channelStr = "C02"
        self.chosenChannel = channelStr
        myWorkingDirectory = path
        if choice == "Hemisphere":
            self.slicing = (slice(None),slice(None),slice(0,256))
        else:
            self.slicing = (slice(None),slice(None),slice(None))
        print(self.slicing, "Self Slicing as ", choice, "\n")
        if Main_Class.os.path.exists(myWorkingDirectory):
            #myWorkingDirectory is the base directory <- alles relativ dazu
            expression_raw = 'Signal/' + channelStr + '/Z<Z,4>_' + channelStr + '.tif'  # applies for example : "Z0001_C01.tif, Z0023..."
            expression_auto = 'Auto/Z<Z,4>_' + 'C01' + '.tif'
            ws = Main_Class.wsp.Workspace('CellMap', directory=myWorkingDirectory);

            #This update is necessary to evoke usage of more than one channel
            ws.update(raw_C01='Signal/C01/Z<Z,4>_C01.tif',
                      raw_C02='Signal/C02/Z<Z,4>_C02.tif',
                      stitched_C01='stitched_C01.npy',
                      stitched_C02='stitched_C02.npy',
                      resampled_C01='resampled_C01.tif',
                      resampled_C02='resampled_C02.tif')
            if self.chosenChannel == "C01":
                ws.update(raw_C01=expression_raw, autofluorescence=expression_auto)
            if self.chosenChannel == "C02":
                ws.update(raw_C02=expression_raw, autofluorescence=expression_auto)

            if Main_Class.os.path.exists(myWorkingDirectory + '/stitched_' + self.chosenChannel + '.tif'):
                expressionStitched = 'stitched_' + self.chosenChannel + '.npy'
                if self.chosenChannel == "C01":
                    ws.update(stitched_C01=expressionStitched)
                if self.chosenChannel == "C02":
                    ws.upate(stitched_C02=expressionStitched)

            if Main_Class.os.path.exists(myWorkingDirectory + '/resampled_' + self.chosenChannel + '.tif'):
                expression_resampled = 'resampled_' + self.chosenChannel + '.tif'
                if self.chosenChannel == "C01":
                    ws.update(resampled_C01=expression_resampled)
                if self.chosenChannel == "C02":
                    ws.update(resampled_C02=expression_resampled)
            ws.info()
            print(ws.filename('cells', postfix='raw_C01'))
            self.ws = ws
            self.myWorkingDirectory = myWorkingDirectory

            print("Worksapce: ", self.ws)
            print("Working dir:", self.myWorkingDirectory)
            print("Channel chosen:", self.chosenChannel)
            return [ws, myWorkingDirectory]
        else:
            print("Path does not exist!")