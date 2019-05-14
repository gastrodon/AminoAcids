# AminoAcids

#### What is this?
AminoAcids is a python api for communicating with amino servers while pretending that you are an app user. This is mostly accomplished by spoofing device configuration headers, though actually generating those is still in progress. It is also for objectifying and organizing amino response data, so that actually doing anything is easier.

#### Why is this?
A member of the Coding101 Amino asked about a public Amino API, and that got my brain thinking. So, I decided to start making one as a fun project.

#### How is this?
As mentioned, this works largely by spoofing device info and login session keys in request headers. These were captured by using the Amino application an android client, and by using [Charles](https://www.charlesproxy.com/) to intercept request and API response data. If you'd like to do this for yourslef, you [should be using android 6 or earlier](https://android-developers.googleblog.com/2016/07/changes-to-trusted-certificate.html)

#### Who is this?
This is currently being developed by [me](https://github.com/basswaver) alone, though pull requests and issues are very much so welcome. You can contact me on Discord at Zero#5200 if you have any questions about the project, or for anything else.

## Usage

Documents are coming soon, when I have something to document. That being said, this is an unstable build and should not be relied on for much (the API will change!). If you'd still like to use it, all of the methods (should) contain docstrings with info to get you started.

## Contributing

This project is just starting (as of whenever this README is pushed), so there are no contributing guidelines yet. Feel free to poke around the source, and feel free to create a pull with some new features or fixes that you'd like to implement.
