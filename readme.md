## Script to create Configuration Profiles for managing OS X Dock

This is a Python script to aid in the creation and maintenance of Dock configuration profiles on OS X.  The script uses a json template to populate the profile.  New profiles can be created and existing profiles can be modified.

__Uaage__
To create a new profile :
```./dock-profile.py --new --input foo.json --profile com.company.dock.foo.mobileconfig --identifier com.company.dock.foo```

To edit an existing profile :
```./dock-profile.py --input foo.json --profile com.company.foo.mobileconfig```