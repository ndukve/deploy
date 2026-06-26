<MissionPackageManifest version="2">
   <Configuration>
      <Parameter name="uid" value="{{ v.tak_userfile_uid }}"/>
      <Parameter name="onReceiveDelete" value="true"/>
      <Parameter name="onReceiveImport" value="true"/>
   </Configuration>
   <Contents>
      <Content ignore="false" zipEntry="MML_Peruskartta.xml"/>
      <Content ignore="false" zipEntry="MML_Ortoilmakuva.xml"/>
      <Content ignore="false" zipEntry="Google_Roadmap.xml"/>
      <Content ignore="false" zipEntry="Google_Hybrid.xml"/>
      <Content ignore="false" zipEntry="Google_Satellite.xml"/>
      <Content ignore="false" zipEntry="Map_defaults.pref"/>
   </Contents>
</MissionPackageManifest>
