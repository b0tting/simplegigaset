# SimpleGigaset
A python wrapper for calling the API of your Gigaset Elements Alarm system

The [Gigaset Elements](www.gigaset.com/gigaset-elements-starter-kit/) is for it's price a very decent alarm system. It connects online and uses an app and website for configuration and monitoring. This allows the system to send you push messages in case of sensors changes.
  
Behind the sc(re)n(e)s both site and app connect to a JSON backend. Why they did not expose this great API, I don't know. Although undocumented, it's easy to follow the HTTP dialog. This SimpleGigaset class wraps the most basic of these functions.    
 
## Function summary
 Some basis functionality is exposed:
- Getting the last few events from your system
- Setting and getting the current system mode
 - Checking if an intrusion is detected, right now!
 
 If you are looking for anything outside of this, consider the [CLI](https://github.com/dynasticorpheus/gigasetelements-cli) 


## Example
One example to show them all. The email and password are the credentials you would use for http://my.gigaset-elements.com.  
```python
simple = SimpleGigaset("b0tting@github.com", "secretpassword")

if simple.is_alarmed():
    print("Oh no! There is an alarm going on RIGHT NOW! Pretend I'm home before the siren goes off!")
    simple.set_mode(SimpleGigaset.MODE_HOME)

print("Are we cool again? %s" % simple.get_current_state()["state"])
