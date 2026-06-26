<MissionPackageManifest version="2">
   <Configuration>
      <Parameter name="uid" value="{{ v.tak_userfile_uid }}"/>
      <Parameter name="name" value="{{ v.tak_server_deployment_name }}"/>
      <Parameter name="onReceiveImport" value="true"/>
      <Parameter name="onReceiveDelete" value="false"/>
   </Configuration>
   <Contents>
      <Content ignore="false" zipEntry="server.pref"/>
      <Content ignore="false" zipEntry="rasenmaeher_ca-public.p12"/>
      <Content ignore="false" zipEntry="{{ v.client_cert_name }}.p12"/>
   </Contents>
</MissionPackageManifest>
