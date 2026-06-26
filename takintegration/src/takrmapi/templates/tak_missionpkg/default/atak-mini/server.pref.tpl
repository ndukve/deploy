<?xml version="1.0" encoding="ASCII" standalone="yes"?>
<preferences>
    <preference version="1" name="cot_streams">
        <entry key="count" class="class java.lang.Integer">1</entry>
        <entry key="description0" class="class java.lang.String">{{ v.tak_server_deployment_name }}</entry>
        <entry key="enabled0" class="class java.lang.Boolean">true</entry>
        <entry key="connectString0" class="class java.lang.String">{{ v.tak_server_public_address }}:8089:ssl</entry>
    </preference>
    <preference version="1" name="com.atakmap.app_preferences">
        <entry key="displayServerConnectionWidget" class="class java.lang.Boolean">true</entry>
        <entry key="caLocation" class="class java.lang.String">cert/rasenmaeher_ca-public.p12</entry>
        <entry key="caPassword" class="class java.lang.String">public</entry>
        <entry key="certificateLocation" class="class java.lang.String">cert/{{ v.client_cert_name }}.p12</entry>
        <entry key="clientPassword" class="class java.lang.String">{{ v.client_cert_password }}</entry>
        <entry key="locationCallsign" class="class java.lang.String">{{ v.client_cert_name }}</entry>
        <!-- Download server profiles on connect and disable tak.gov default maps -->
        <entry key="deviceProfileEnableOnConnect" class="class java.lang.Boolean">true</entry>
        <entry key="eud_api_sync_mapsources" class="class java.lang.Boolean">false</entry>
        <entry key="atakPluginScanninOnStartup" class="class java.lang.Boolean">true</entry>
   </preference>
</preferences>
