# Minor-Projects
<body>
  <h2>YouTube Video Downloader</h2>
  <p>This program allows users to download YouTube videos and extract their audio as MP3 files. It uses the <code>tkinter</code> library for the GUI, <code>pytube</code> for downloading videos, and <code>moviepy</code> for audio extraction.</p>
  <h3>Requirements</h3>
  <ul>
    <li>Python 3.x</li>
    <li>tkinter</li>
    <li>pytube</li>
    <li>moviepy</li>
    <li>shutil</li>
  </ul>
  <h3>Usage</h3>
  <p>Run the script and use the GUI to:</p>
  <ol>
    <li>Enter the URL of the YouTube video.</li>
    <li>Select the path to download the video.</li>
    <li>Click the "Download" button to start downloading.</li>
  </ol>

  <h2>Credit Card Validator</h2>
  <p>This program validates credit card numbers using the Luhn algorithm. The algorithm checks if a given credit card number is valid by performing a series of mathematical operations.</p>
  <h3>Requirements</h3>
  <ul>
    <li>Python 3.x</li>
  </ul>
  <h3>Usage</h3>
  <p>Run the script and enter a credit card number to check its validity.</p>

  <h2>PDF Invoice Generator</h2>
  <p>This program generates a PDF invoice from a list of medicines and their quantities. It uses the <code>tkinter</code> library for the GUI and <code>FPDF</code> for creating the PDF.</p>
  <h3>Requirements</h3>
  <ul>
    <li>Python 3.x</li>
    <li>tkinter</li>
    <li>FPDF</li>
  </ul>
  <h3>Usage</h3>
  <p>Run the script and use the GUI to:</p>
  <ol>
    <li>Select medicines and their quantities.</li>
    <li>Enter the customer's name.</li>
    <li>Click the "Generate Invoice" button to create the PDF invoice.</li>
  </ol>

  <h2>QR Code Generator</h2>
  <p>This program generates QR codes from a given link and displays them using a graphical interface. It uses the <code>tkinter</code> library for the GUI, <code>pyqrcode</code> for generating QR codes, and <code>PIL</code> for image handling.</p>
  <h3>Requirements</h3>
  <ul>
    <li>Python 3.x</li>
    <li>tkinter</li>
    <li>pyqrcode</li>
    <li>PIL (Pillow)</li>
  </ul>
  <h3>Usage</h3>
  <p>Run the script and use the GUI to:</p>
  <ol>
    <li>Enter the name of the link (used as the file name).</li>
    <li>Enter the URL to be converted to a QR code.</li>
    <li>Click the "Generate" button to create and display the QR code.</li>
  </ol>

  <h2>Student Management System</h2>
  <p>This program is a simple student management system that allows users to add, update, delete, and view student data. It uses the <code>tkinter</code> library for the GUI and <code>mysql-connector-python</code> for database operations.</p>
  <h3>Requirements</h3>
  <ul>
    <li>Python 3.x</li>
    <li>tkinter</li>
    <li>mysql-connector-python</li>
    <li>MySQL server</li>
  </ul>
  <h3>Usage</h3>
  <p>Run the script and use the GUI to:</p>
  <ol>
    <li>Add new student data by entering the name, address, age, and phone number, then clicking "Add Data".</li>
    <li>Delete student data by selecting a student from the list and clicking "Delete Data".</li>
    <li>Update student data by selecting a student from the list, modifying the details, and clicking "Update Data".</li>
    <li>Create the students table in the database by clicking "Create Table".</li>
  </ol>
  <p>The student data is displayed in a tree view for easy management.</p>

  <h3>Note</h3>
  <p>Ensure all dependencies are installed using <code>pip</code> before running the scripts:</p>
  <pre><code>pip install tkinter pytube moviepy FPDF pyqrcode pillow mysql-connector-python</code></pre>
</body>
</html>
