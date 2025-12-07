### This folder hosts statistics about the adoption of third-party SDKs in third-party apps.

All results are presented in the "scan_results.json". 

401 apps are collected from the top 300 apps from both the Google Play Store and Wandoujia (for the China market) after removing duplication, based on the ranking as of June 2023.

From these 401 apps, we extract the package files and retrieve all the libraries. As a result, 67032 libraries are found. In which 67032 libraries, 60648 libraries are in ".aar" format (i.e., Android libraries). 

We then filter the ".aar" libraries to only consider the libraries that are from our pre-identified 158 SDKs (because an Android library does not necessarily constitute an Android SDK), and finally, 2606 occurrences of Android SDKs. 

Based on the above statistics, we come to our conclusion that our observation shows that each third-party app embeds an average of 9 SDKs.
