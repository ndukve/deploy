# openLDAP with PVARKI defaults

## Used as git submodule

This repo is used as submodule in https://github.com/pvarki/docker-rasenmaeher-integration
it is probably a good idea to handle all development via it because it has docker composition
for bringin up all the other services rasenmaeher-api depends on

## Local testing

1. Run `docker-compose -f docker-compose-local.yml up`

Execute inside openldap container with uid of created user:

```
ldapsearch -LL -Y EXTERNAL -H ldapi:/// "(uid=testuser)" -b dc=example,dc=org memberOf
```
