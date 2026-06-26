Packing APK to be compliant with Update Server format

#get the files from assets\apks\ in your android folder.  // tak.gov civ release (including plugins)

#zip up the .png file and .inf file and name it as product.infz

#copy the files to folder and edit access and user rights#

cd /opt/tak/webcontent/

sudo mkdir update

cd /tmp/update/

sudo mv FILENAME /opt/tak/webcontent/update

sudo chmod 777 /opt/tak/webcontent/update -R

sudo chown tak:tak /opt/tak/webcontent/update -R

sudo systemctl restart takserver



---------------------------------------------------------

Files that are needed

APK and PNG for every plugin

products.inf that includes all the information of the plugins

PNG's and products.inf are combined to a .zip file that is renamed as.infz


---------------------------------------------------------

EUD config's to allow the update server to work server.pref file:

<entry key="deviceProfileEnableOnConnect" class="class java.lang.Boolean">true</entry>
<entry key="eud_api_sync_mapsources" class="class java.lang.Boolean">false</entry>
<entry key="atakPluginScanninOnStartup" class="class java.lang.Boolean">true</entry>
<entry key="atakUpdateServerUrl" class="class java.lang.String">https://IP:8443/update</entry>
<entry key="appMgmtEnableUpdateServer" class="class java.lang.Boolean">true</entry>
