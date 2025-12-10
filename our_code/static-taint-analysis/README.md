To run static taint analysis on Appshark, simple download the Appshark (hosted on [GitHub](https://github.com/bytedance/appshark)), install the necessary dependencies.

After that, you will be able to run it by executing the script "run.sh" in the root directory.

To perform static analysis, you will need to do two things: 

(1) Prepare an apk file. For our SDK assessment, simply creating a blank app and install/embed the SDK would be fine.

(2) Write a configuration file to include all the rules (specifying sink, source, and other options). Our rules can be found in the "rules" directory. 

A sample of the configuration is given below:

'''
{
	"apkPath": "/Users/analysis/apks/test.apk",  // the path of the apk to be analyzed
	"out": "/Users/analysis/output",             // the path for output
	"rules": "adInfo.json, adInfo1.json, AndroidID.json, serialNoInfo.json",
	                                             // include all the rules you want to apply
	"rulePath": "./rules",                       // specify the folder for all rule json files
	"maxPointerAnalyzeTime": 300,                // timeout by default
	"debugRule": ""                              // debug rule, leave it blank if you don't have one

}
'''

You may follow the GitHub of AppShark for detailed tutorials.