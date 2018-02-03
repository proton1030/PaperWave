# PaperWave

__Sound Generative Web App Based On Paper Drawing Interpretations__

This project is about a web-based application which takes pictures of hand drawings on templates as input and produce sound as the output. This app was aimed to discover more about  creating sound using tangible medium instead of using touchscreen or computer. By mapping the hand-drawn graphs and curves to corresponding sounds, the output of this procedure might be intuitive and surprising at the same time. Also due to the fact that users can only hear sound after they've uploaded their drawings, the loop of creating-hearing-modifying is actually broken, which makes the user actually decide and care more about their decisions and produce more interesting results on a certain level.

[![pic](https://i.vimeocdn.com/video/681138829_1280x720.jpg)](https://vimeo.com/254080662)



## System Design and Implementation

The app consists of two main parts: the front-end which is more about the UI and interaction with users, and the back-end which is about the sound generation and handling requests from the front-end. The sound generation has two generation modes: the sequencer mode and the waveform mode.


\begin{figure}[ht!]
\includegraphics[width=\linewidth]{layout.png}
\caption{Structure of the web app's design}
\label{fig:bee} %% The label
\end{figure}


\subsection{Front-end Design} 
\subsubsection{UI/UX design}
The front-end UI basically consists of two main parts: the uploading section and the display section. At the uploading section, the user is available to upload a sketch photo drawn by themselves through a desktop computer, or take a photo on the fly by using a mobile device instead, which makes this whole creation process work more seamlessly. For the display section, there'll be corresponding results according to the sketch that you've uploaded: as for the sequencer mode, it will eventually show the grid extracted from the sequencer template and its corresponding sound result. As for the waveform mode, there'll be a rough visualization about how the sound is actually generated with some description text. It'll display the particles' moving trajectory in the vector field and different sound results using different approaches of synthesis based on user input. The color scheme works fine and Helvetica Neue was chosen as the font type since a sans-serif font would be more fitting to this app.\par
In order to provide convenience for different usage scenarios, there'll be two different types of layout while viewing the web app on a desktop browser and on a mobile phone (Fig. \ref{fig:ui}). The reason for splitting the UI into desktop version and mobile version is to deal with two different user case scenarios: users can download the templates on the computer and print them out, but it's always easy to get the results just by taking photos using mobile devices. Overall, the UI layout is not counter-intuitive and users actually know what to do as soon as they opened the app based on the results of a small-scale demo test. \par

\begin{figure}[ht!]
\centering
\includegraphics[width=\linewidth]{UI.png}
\caption{Hardware Design Layout in 3D Modeling Representation}
\label{fig:ui} %% The label
\end{figure}

\subsubsection{Technology details}
The front end web page design used Jade+SASS to get a higher coding performance and clarity for reading. JQuery was used for the communication between the front-end and the back-end and AJAX requests are the most used requests since all the multimedia materials have to be fetched from the server during the generation process. An asynchronous fetching method was adopted in order to let users see the process on the fly and decrease the waiting duration. Other kinds of common front-end implementations (like binding event-listeners for music player) will not be discussed further.

\subsection{Back-end Design} 
The back-end of this project consists of two main parts: A server for communicating between the front-end and the generation process and A generation part which is a python process.

\subsubsection{server design}
The server was constructed using Node.js and Express.js, which grant a variety of communication methods and high customizability. The server listened to the port and wait for requests from the front-end. It receives files from front-end and feed it into a python process which will eventually save the output files to a unique labeled directory on the server. The server will send different files back to the front-end based on different kinds of front-end requests.

\subsubsection{Python process}
The python process accounts for the generation of the sounds and corresponding visual representations also consists of several major parts: Image recognizing and QRcode extraction, sequencer mode sound generation, waveform mode generation, mixing output using different approaches.

\paragraph{Image recognization and QRcode extraction}
The QRcode on the templates serves for two main reasons: one is to determine the area for creation on the template and the other is to decide which template is this. After users uploaded their modified template (See fig. \ref{fig:template}) to the server, the image will first be processed in order to get a higher robustness by adjusting contrast, brightness and blurness. OpenCV framework was used later to extract the contour of the picture. By deciding whether there's a relation between the contours that the area ratio equals 9:25:49 (which stands for the area of each part in a QRcode locator), which determines the location of QRcode locators in this photo. once it found 6 results in one picture and calculating the variance matrix of cross distance among the 6, it'll correct the perspective of the picture and crop the useful area out, also recognizing the QRcode on the bottom right in order to decide which synthesis method will be used later.

\begin{figure}[ht!]
\centering
\includegraphics[width=\linewidth]{chiptune.jpg}
\caption{A template for chiptune sound sequencing}
\label{fig:template} %% The label
\end{figure}

\paragraph{Sequencer mode}
Once the QRcode decoded and recognized as sequencer mode, the grid area picture restricted by the QR locators will then be interpreted further more. Since the row and column quantity of the template is known, we simply divide the whole area into blocks which stands for whether a sound or a condition is triggered. According to the decoded QRcode information, different sound sets are used to create sound sequence. User can adjust the sequence tempo by painting the corresponding speed grid black. After filling in the grid with black markers, the decision is simply made by running a threshold test on each block to determine if it's been switched on. Then the sound set samples will be mapped to corresponding time locations and return a mix of each row's output. 

\paragraph{Waveform mode}
If the result for QRcode is 'waveform', the picture will be dissected and fed into the waveform process. There are two main path for the waveform mode sound to be generated: one is wavetable synthesis, the other is particle movement simulation. As for the wavetable mode, user's hand-drawn curve will be treated as a waveform snippet and be duplicated till the end of the sound. Also, the curve itself will be translated as an envelope for various modulation: As for the pitch modulation, the higher the the current point is, the higher the pitch, the more duplication happens in one second of final output sound file, and vice versa. As for amplitude modulation, the envelope will simply used as the amplitude envelope for the entire output sound waveform. There's also a morph table function, where multiple curves that uploaded by users can be used. Each one of them has a possibility of gradually morphing into another during the duplication with a sinusoidal or square morph ratio curve.\par
The other type of synthesis is basically like a physical simulation, where the hand-drawn curve is firstly converted into a contour map by running a Gaussian low-pass filter over the image iteratively (See Fig. \ref{fig:process}). By doing this, the grayscale of the picture can be regarded as altitude of a surface which is not flat. Then, a certain amount of particle objects are randomly put on this surface. By comparing its altitude with its surrounding eight pixel's altitude, it'll always find the path with the largest altitude difference. Eventually, it'll gain acceleration by doing this step iteratively and changing its speed like real world objects. There's also a mechanism for detecting if the particle's speed is lower than than certain threshold for certain number of iterations, the particle will be removed and a new particle will be instantiated. By updating the particles' location, we can get several velocity sequences and map that into sound.

\paragraph{mixing and output}
After these two different approaches in the waveform mode, the results will be combined using amplitude multiplication or just switching between each other on a random basis. All modes' output will be saved into a folder with a random generated name which will be queried by the front-end.

\begin{figure}[ht!]
\centering
\includegraphics[width=\linewidth]{process.png}
\caption{The process of synthesizing using particles motion simulation}
\label{fig:process} %% The label
\end{figure}

