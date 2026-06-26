<?xml version="1.0" encoding="ASCII" standalone="yes"?>
<preferences>
  <preference version="1" name="cot_streams">
    <entry key="count" class="class java.lang.Integer">1</entry>
    <entry key="description0" class="class java.lang.String">{{ v.tak_server_deployment_name }}</entry>
    <entry key="enabled0" class="class java.lang.Boolean">true</entry>
    <entry key="connectString0" class="class java.lang.String">{{ v.tak_server_public_address }}:8089:ssl</entry>
    <entry key="caLocation0" class="class java.lang.String">cert/rasenmaeher_ca-public.p12</entry>
    <entry key="caPassword0" class="class java.lang.String">public</entry>
    <entry key="certificateLocation0" class="class java.lang.String">cert/{{ v.client_cert_name }}.p12</entry>
    <entry key="clientPassword0" class="class java.lang.String">{{ v.client_cert_password }}</entry>
  </preference>
  <preference version="1" name="gov.tak.taktracker_preferences">
    <entry key="callsign" class="class java.lang.String">{{ v.client_cert_name }}</entry>
    <entry key="role" class="class java.lang.String">Team Member</entry>
    <!-- hidden, set if needed <entry key="team" class="class java.lang.String">Dark Green</entry> -->
   </preference>
</preferences>
