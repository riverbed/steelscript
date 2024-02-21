# TEST RESULTS

## Test - Feb. 2024 - OK

### Goal

- validate update 24.2.1

### Functional test plan scope

- downloading packets
- running reports for specific Host Groups
- running reports for filtered conversations

### Test environment details

- Linux container
- Python 3.12

### Samples

- SteelScript about

```
# steel about

Installed SteelScript Packages
Core packages:
  steelscript                               24.2.1
  steelscript.appresponse                   24.2.1
  steelscript.cacontroller                  24.2.1
  steelscript.cmdline                       24.2.1
  steelscript.netim                         24.2.1
  steelscript.netprofiler                   24.2.1
  steelscript.packets                       24.2.1
  steelscript.scc                           24.2.1
  steelscript.steelhead                     24.2.1
  steelscript.wireshark                     24.2.1

Application Framework packages:
  None

REST tools and libraries:
  reschema                                  2.0
  sleepwalker                               2.0

Paths to source:
  /src-dev/steelscript
  /src-dev/steelscript-appresponse
  /src-dev/steelscript-client-accelerator-controller
  /src-dev/steelscript-cmdline
  /src-dev/steelscript-netim
  /src-dev/steelscript-netprofiler
  /src-dev/steelscript-packets
  /src-dev/steelscript-scc
  /src-dev/steelscript-steelhead
  /src-dev/steelscript-wireshark
  /usr/local/lib/python3.12/site-packages

(add -v or --verbose for further information)
```

- AppResponse hostgroups

```
# python examples/appresponse-examples/print_hostgroups-formatted.py your_app_reponse_fqdn -u 'your_username' -p 'your_password'

id    name                   active    definition                                                                                                           
------------------------------------------------------------------------------------------------------------------------------------------------------------
1     Default-10.x.x.x       True      ['10.0.0.0-10.255.255.255']                                                                                          
2     Default-Internet       True      ['1.0.0.0-9.255.255.255', '11.0.0.0-172.15.255.255', '172.32.0.0-192.167.255.255', '192.169.0.0-255.255.255.255']    
3     Default-172.x.x.x      True      ['172.16.0.0-172.31.255.255']                                                                                        
4     Default-192.168.x.x    True      ['192.168.0.0-192.168.255.255']    
```


## Test - Nov. 2020 - OK

### Goal

- validate recent version of key dependencies

### Functional test plan scope

- downloading packets
- running reports for specific Host Groups
- running reports for filtered conversations

### Test environment details

Linux box with python 3.7, steelscript 2.0 and modules deployed by pip (not confirmed)

- Speficic python lib deployed by pip 

requests == 2.25.0 
urllib3 == 1.26.2
