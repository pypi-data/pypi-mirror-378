<h1 align="center">Discard Rest APIs</h1>

<p align="center">
  <img src="https://img.shields.io/npm/v/discard-api" alt="NPM Version">
  <img src="https://img.shields.io/badge/Made%20with-%E2%9D%A4-red" alt="Made with Love">
  <img src="https://img.shields.io/badge/Open%20Source-%F0%9F%8C%90-blue" alt="Open Source">
</p>

<p align="center">
  A hub of RESTful APIs for developers, providing 500+ powerful endpoints across multiple categories.<br>
  From downloaders and AI tools to image processing, games, and converters - everything you need to elevate your applications to new heights.
</p>

	
<div align="center">

[![Go Reference](https://pkg.go.dev/badge/github.com/GlobalTechInfo/discard-api.svg)](https://pkg.go.dev/github.com/GlobalTechInfo/discard-api)
[![Go Report Card](https://goreportcard.com/badge/github.com/GlobalTechInfo/discard-api)](https://goreportcard.com/report/github.com/GlobalTechInfo/discard-api)
[![GitHub release](https://img.shields.io/github/release/GlobalTechInfo/discard-api.svg)](https://github.com/GlobalTechInfo/discard-api/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

</div>


## Features

- **Developer-Friendly** - Intuitive endpoints with clear documentation
- **Extensive Collection** - 500+ ready-to-use REST APIs across 30+ categories
- **Affordable Pricing** - Competitive rates with many free endpoints
- **Blazing Fast** - Optimized for speed and reliability
- **Seamless Integration** - Works with any programming language or framework
- **Complete Documentation** - Detailed guides and examples for every API

## API Categories

Discard offers APIs across numerous categories including:

- **Islamic** - Quran, Surah, Hadith and more
- **News** - Latest news endpoints of many platforms
- **Downloader** - Download content from many platforms
- **AI Tools** - Many ai models and llms
- **Image Processing** - Filters, effects, and more
- **Stalking** - Social media data extraction
- **Searching** - Advanced search apis across platforms
- **Converters** - Format and convert your data
- **And many more!**

Explore our complete catalog at [discardapi.dpdns.org](https://discardapi.dpdns.org)

## Getting Started with Discard Rest APIs


**Welcome to Discard Rest APIs, your one-stop solution for seamless API integrations! Our extensive collection of APIs is designed for developers building apps, businesses enhancing services, or tech enthusiasts experimenting with new ideas.**

### Step 1: Sign Up & Get Your API Key

- Create an account to access our API dashboard. Signing up is quick and easy, providing instant access to hundreds of powerful APIs.

### Step 2: Choose an API

- Browse our comprehensive API library and select the API that fits your needs. Each API includes detailed documentation with endpoints, parameters, and response formats.

### Step 3: Make Your First API Call

- With your API key in hand, you're ready to start! All our APIs follow REST principles and are designed for simple, intuitive integration.

### Step 4: Integrate the API

- Easily incorporate our APIs into your existing systems using the provided code examples for popular languages like JavaScript, Python, PHP and more.

### Step 5: Upgrade for More Features

- For extensive usage and advanced features, upgrade to a PRO or VIP plan offering higher limits, faster response times, and premium feature access.

---


## 🚀 Quick Start

### Account Registration

**1: Create Account (🔵POST)**
```nginx
POST https://discardapi.dpdns.org/api/auth/signup
{
  "name": "John Doe",
  "email": "john@example.com", 
  "password": "strongpassword123"
}
```

**Response (200)**
```json
{
  "status": true,
  "creator": "Qasim Ali 🩷",
  "success": true,
  "message": "Verification code sent"
}
```

### 2: Verify Account (🔵POST)
```nginx
POST https://discardapi.dpdns.org/api/auth/verify-signup
{
  "email": "john@example.com",
  "code": "123456"
}
```

**Response (201)**
```json
{
  "status": true,
  "creator": "Qasim Ali 🩷", 
  "success": true,
  "message": "Account created successfully",
  "api_key": "abcd1234efgh5678"
}
```

Get started in seconds. Add your **API key** to any endpoint and receive structured JSON responses with comprehensive error handling.

### ⚙️ Request Format  
```http
GET https://discardapi.dpdns.org/api/endpoint?apikey=YOUR_KEY
```
**Request Parameters**

| Name   | Type   | Required | Description                         |
| ------ | ------ | -------- | ----------------------------------- |
| apikey | string | ✅        | Your API key                        |


```json

{
  "status": true,
  "creator": "Qasim Ali 🩷",
  "result": {"..."}
}
```
---

### 📌 API Examples

---

### AlJazeera Headlines (🟢GET)

**Endpoint**
```nginx
GET https://discardapi.dpdns.org/api/aljazeera?apikey=YOUR_API_KEY
```
**Request Parameters**

| Name   | Type   | Required | Description                         |
| ------ | ------ | -------- | ----------------------------------- |
| apikey | string | ✅        | Your API key                        |

**Response**
```json
{
  "status": true,
  "creator": "Qasim Ali 🩷",
  "result": [
    {
      "id": "article-id",
      "title": "Breaking news headline",
      "image": "https://www.aljazeera.com/someimage.jpg",
      "url": "https://www.aljazeera.com/news/2025/09/20/article-id"
    }
  ],
  "timestamp": "2025-09-20 03:04 PM"
}
```

### Full Article (🟢GET)

**Endpoint**
```nginx

GET https://discardapi.dpdns.org/api/aljazeera/article?apikey=YOUR_API_KEY&url=https://www.aljazeera.com/news/2025/09/20/article-id
```
**Request Parameters**

| Name   | Type   | Required | Description                         |
| ------ | ------ | -------- | ----------------------------------- |
| apikey | string | ✅        | Your API key                        |
| url    | string | ✅        | Link/Url of the article             |

**Response**
```json

{
  "status": true,
  "creator": "Qasim Ali 🩷",
  "result": {
    "title": "Breaking news headline",
    "subhead": "Article subhead",
    "content": "Full article text...",
    "image": "https://www.aljazeera.com/someimage.jpg",
  },
  "timestamp": "2025-09-20 03:04 PM"
}
```
**Usage cURL**
```nginx
curl "https://discardapi.dpdns.org/api/aljazeera?apikey=YOUR_API_KEY"

curl "https://discardapi.dpdns.org/api/aljazeera/article?apikey=YOUR_API_KEY&url=https://www.aljazeera.com/news/2025/09/20/article-id"
```
**Usage Node.js**
```js

import axios from "axios";

async function getArticles() {
  const res = await axios.get("https://discardapi.dpdns.org/api/aljazeera", {
    params: { apikey: "YOUR_API_KEY" }
  });
  console.log(res.data);
}

async function getArticleDetails() {
  const res = await axios.get("https://discardapi.dpdns.org/api/aljazeera/article", {
    params: {
      apikey: "YOUR_API_KEY",
      url: "https://www.aljazeera.com/news/2025/09/20/article-id"
    }
  });
  console.log(res.data);
}

getArticles();
getArticleDetails();
```
**Usage Python**
```py
import requests

base = "https://discardapi.dpdns.org/api"

res = requests.get(f"{base}/aljazeera", params={"apikey": "YOUR_API_KEY"})
print(res.json())

res = requests.get(f"{base}/aljazeera/article", params={
    "apikey": "YOUR_API_KEY",
    "url": "https://www.aljazeera.com/news/2025/09/20/article-id"
})
print(res.json())
```
**Usage Go**
```go
package main

import (
	"fmt"
	"io/ioutil"
	"net/http"
)

func main() {
	resp, _ := http.Get("https://discardapi.dpdns.org/api/aljazeera?apikey=YOUR_API_KEY")
	body, _ := ioutil.ReadAll(resp.Body)
	fmt.Println(string(body))

	resp, _ = http.Get("https://discardapi.dpdns.org/api/aljazeera/article?apikey=YOUR_API_KEY&url=https://www.aljazeera.com/news/2025/09/20/article-id")
	body, _ = ioutil.ReadAll(resp.Body)
	fmt.Println(string(body))
}
```
**Usage PHP**
```php
<?php
$articles = file_get_contents("https://discardapi.dpdns.org/api/aljazeera?apikey=YOUR_API_KEY");
echo $articles;

$article = file_get_contents("https://discardapi.dpdns.org/api/aljazeera/article?apikey=YOUR_API_KEY&url=https://www.aljazeera.com/news/2025/09/20/article-id");
echo $article;
?>
```
**Usage Java**
```java
import okhttp3.*;

public class Main {
    public static void main(String[] args) throws Exception {
        OkHttpClient client = new OkHttpClient();

        Request request = new Request.Builder()
            .url("https://discardapi.dpdns.org/api/aljazeera?apikey=YOUR_API_KEY")
            .build();

        try (Response response = client.newCall(request).execute()) {
            System.out.println(response.body().string());
        }

        Request articleRequest = new Request.Builder()
            .url("https://discardapi.dpdns.org/api/aljazeera/article?apikey=YOUR_API_KEY&url=https://www.aljazeera.com/news/2025/09/20/article-id")
            .build();

        try (Response response = client.newCall(articleRequest).execute()) {
            System.out.println(response.body().string());
        }
    }
}
```

**Usage Swift**
```swift
import Foundation

let url = URL(string: "https://discardapi.dpdns.org/api/aljazeera?apikey=YOUR_API_KEY")!

let task = URLSession.shared.dataTask(with: url) { data, _, error in
    if let error = error {
        print("Error:", error)
        return
    }
    if let data = data, let response = String(data: data, encoding: .utf8) {
        print("Articles:", response)
    }
}
task.resume()

let detailURL = URL(string: "https://discardapi.dpdns.org/api/aljazeera/article?apikey=YOUR_API_KEY&url=https://www.aljazeera.com/news/2025/09/20/article-id")!

let detailTask = URLSession.shared.dataTask(with: detailURL) { data, _, error in
    if let error = error {
        print("Error:", error)
        return
    }
    if let data = data, let response = String(data: data, encoding: .utf8) {
        print("Article Detail:", response)
    }
}
detailTask.resume()
```
---

---

### Markdown → HTML (🟣ALL)

**Endpoint**
```nginx
POST https://discardapi.dpdns.org/api/markdown?apikey=YOUR_API_KEY
```
**Usage cURL**

1. JSON body

```bash
curl -X POST "https://discardapi.dpdns.org/api/markdown?apikey=YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"markdown": "# Hello World\nThis is a test"}'
   ```
2. Form-urlencoded
```nginx
curl -X POST "https://discardapi.dpdns.org/api/markdown" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "apikey=YOUR_API_KEY&markdown=# Hello World\nThis is a test"
```

3. Plain text
```nginx
curl -X POST "https://discardapi.dpdns.org/api/markdown?apikey=YOUR_API_KEY" \
  -H "Content-Type: text/plain" \
  --data "# Hello World\nThis is a test"
```

4. File upload
```nginx
curl -X POST "https://discardapi.dpdns.org/api/markdown?apikey=YOUR_API_KEY" \
  -F "file=@example.md"
```
---

---

### Update Product (🟤PUT)

**Endpoint**
```nginx
PUT https://discardapi.dpdns.org/api/update/product?id={product_id}&apikey={your_api_key}
```
**Request Parameters**

**Query Parameters**
| Name   | Type   | Required | Description            |
|--------|--------|----------|------------------------|
| apikey | string | ✅       | Your API key           |
| id     | int    | ✅       | Product ID to update   |

**Body Parameters (JSON or Form Data)**
| Name        | Type      | Required | Description                     |
|-------------|-----------|----------|---------------------------------|
| id          | int/string| ✅       | Must match the `id` in query    |
| title       | string    | ✅       | Product title                   |
| price       | string    | ✅       | Product price                   |
| description | string    | ✅       | Product description             |
| category    | string    | ✅       | Product category                |
| image       | string    | ✅       | Product image URL               |

**Response Format**
```json
{
  "status": true,
  "creator": "Qasim Ali 🩷",
  "result": {
    "id": 1,
    "title": "Updated Product",
    "price": "15.99",
    "description": "Updated description here",
    "category": "electronics",
    "image": "https://example.com/image.png"
  }
}
```

**Usage cURL**
```bash
curl -X PUT "https://discardapi.dpdns.org/api/update/product?id=1&apikey=your_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "title": "Updated Product",
    "price": "15.99",
    "description": "Updated description here",
    "category": "electronics",
    "image": "https://example.com/image.png"
  }'
```
**Usage Node.js**
```js
import axios from "axios";

const url = "https://discardapi.dpdns.org/api/update/product?id=1&apikey=your_api_key";

axios.put(url, {
  id: 1,
  title: "Updated Product",
  price: "15.99",
  description: "Updated description here",
  category: "electronics",
  image: "https://example.com/image.png"
})
.then(res => console.log(res.data))
.catch(err => console.error(err.response?.data || err.message));
```
**Usage Python**
```py
import requests

url = "https://discardapi.dpdns.org/api/update/product"
params = {"id": 1, "apikey": "your_api_key"}
data = {
    "id": 1,
    "title": "Updated Product",
    "price": "15.99",
    "description": "Updated description here",
    "category": "electronics",
    "image": "https://example.com/image.png"
}

res = requests.put(url, params=params, json=data)
print(res.json())
```

**Usage PHP**
```php
<?php
$url = "https://discardapi.dpdns.org/api/update/product?id=1&apikey=your_api_key";

$data = [
  "id" => 1,
  "title" => "Updated Product",
  "price" => "15.99",
  "description" => "Updated description here",
  "category" => "electronics",
  "image" => "https://example.com/image.png"
];

$options = [
  "http" => [
    "method"  => "PUT",
    "header"  => "Content-Type: application/json",
    "content" => json_encode($data)
  ]
];

$context  = stream_context_create($options);
$response = file_get_contents($url, false, $context);
echo $response;
?>
```
---

---

### 🎴 Vignette Image Upload (🔵POST)

**Endpoint**
```nginx
POST https://discardapi.dpdns.org/api/image/vignette
```

**Request Parameters**

| Name      | Type   | Required | Description                                         |
|-----------|--------|----------|-----------------------------------------------------|
| apikey    | string | ✅       | Your API key                                        |
| file      | file   | ✅       | Image file to process                               |
| intensity | float  | ❌       | Vignette intensity (0.1–1.0, default: `0.5`)        |
| shape     | string | ❌       | Shape of vignette → `"circle"` or `"rectangle"`     |
| color     | string | ❌       | Vignette color → `"black"` or HEX code (`#rrggbb`)  |


**Response**
- Success (Image Stream)

- Content-Type: image/jpeg (or image/png depending on input)

- Response is the processed image.

**🔹Usage cURL**
```bash
curl -X POST "https://discardapi.dpdns.org/api/image/vignette" \
  -F "apikey=your_api_key" \
  -F "file=@input.jpg" \
  -F "intensity=0.8" \
  -F "shape=circle" \
  -F "color=#000000" \
  --output output.jpg

```
**🔹Usage JavaScript**
```js

import axios from "axios";
import fs from "fs";
import FormData from "form-data";

const form = new FormData();
form.append("apikey", "your_api_key");
form.append("file", fs.createReadStream("input.jpg"));
form.append("intensity", "0.8");
form.append("shape", "circle");
form.append("color", "#000000");

axios.post("https://discardapi.dpdns.org/api/image/vignette", form, {
  headers: form.getHeaders(),
  responseType: "stream"
})
.then(res => {
  const writer = fs.createWriteStream("output.jpg");
  res.data.pipe(writer);
})
.catch(err => console.error(err.response?.data || err.message));
```
**Usage Python**
```py
import requests

url = "https://discardapi.dpdns.org/api/image/vignette"
files = {"file": open("input.jpg", "rb")}
data = {
    "apikey": "your_api_key",
    "intensity": "0.8",
    "shape": "circle",
    "color": "#000000"
}

res = requests.post(url, files=files, data=data, stream=True)

if res.headers.get("Content-Type", "").startswith("image/"):
    with open("output.jpg", "wb") as f:
        for chunk in res.iter_content(1024):
            f.write(chunk)
else:
    print(res.json())  # error JSON
```

**Usage PHP**
```php
<?php
$url = "https://discardapi.dpdns.org/api/image/vignette";

$postfields = [
  "apikey" => "your_api_key",
  "file" => new CURLFile("input.jpg"),
  "intensity" => "0.8",
  "shape" => "circle",
  "color" => "#000000"
];

$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);
curl_setopt($ch, CURLOPT_POST, 1);
curl_setopt($ch, CURLOPT_POSTFIELDS, $postfields);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$response = curl_exec($ch);
$contentType = curl_getinfo($ch, CURLINFO_CONTENT_TYPE);
curl_close($ch);

if (strpos($contentType, "image/") === 0) {
    file_put_contents("output.jpg", $response);
} else {
    echo $response; // JSON error
}
?>
```

**Usage Go**
```go
package main

import (
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
	"strings"
)

func main() {
	url := "https://discardapi.dpdns.org/api/image/vignette"

	// Create multipart form
	body := &strings.Builder{}
	writer := multipart.NewWriter(body)

	// Add API key and params
	_ = writer.WriteField("apikey", "your_api_key")
	_ = writer.WriteField("intensity", "0.8")
	_ = writer.WriteField("shape", "circle")
	_ = writer.WriteField("color", "#000000")

	// Add file
	file, err := os.Open("input.jpg")
	if err != nil {
		panic(err)
	}
	defer file.Close()

	part, err := writer.CreateFormFile("file", "input.jpg")
	if err != nil {
		panic(err)
	}
	_, _ = io.Copy(part, file)
	writer.Close()

	// Send request
	req, _ := http.NewRequest("POST", url, strings.NewReader(body.String()))
	req.Header.Set("Content-Type", writer.FormDataContentType())

	client := &http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()

	// Check if response is image
	contentType := resp.Header.Get("Content-Type")
	if strings.HasPrefix(contentType, "image/") {
		out, _ := os.Create("output.jpg")
		defer out.Close()
		_, _ = io.Copy(out, resp.Body)
		fmt.Println("✅ Saved processed image to output.jpg")
	} else {
		// Print JSON error
		errResp, _ := io.ReadAll(resp.Body)
		fmt.Println(string(errResp))
	}
}
```
---

---

### 📦 Catbox File Upload API (🔵POST)

**Endpoint:**
```nginx
POST https://discardapi.dpdns.org/api/catbox
```
**Request Parameters**

| Name   | Type   | Required | Description                         |
| ------ | ------ | -------- | ----------------------------------- |
| apikey | string | ✅        | Your API key                        |
| file   | file   | ✅        | File to upload (any type supported) |

**Response Format**
```json
{
  "status": true,
  "creator": "Qasim Ali 🩷",
  "result": {
    "url": "https://files.catbox.moe/abcd123.zip"
}
```

**Usage cURL**

```bash

curl -X POST "https://discardapi.dpdns.org/api/catbox" \
  -F "apikey=your_api_key" \
  -F "file=@example.zip"
```

**Usage JavaScript**
```js
import axios from "axios";
import FormData from "form-data";
import fs from "fs";

const form = new FormData();
form.append("apikey", "your_api_key");
form.append("file", fs.createReadStream("example.zip"));

const res = await axios.post("https://discardapi.dpdns.org/api/catbox", form, {
  headers: form.getHeaders()
});

console.log(res.data);
```

**Usage Python**

```py
import requests

url = "https://discardapi.dpdns.org/api/catbox"
files = {"file": open("example.pdf", "rb")}
data = {"apikey": "your_api_key"}

res = requests.post(url, files=files, data=data)
print(res.json())
```

**Usage PHP**

```php

<?php
$ch = curl_init("https://discardapi.dpdns.org/api/catbox");

$post = [
    "apikey" => "your_api_key",
    "file" => new CURLFile("example.docx")
];

curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $post);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);

$response = curl_exec($ch);
curl_close($ch);

echo $response;
?>
```

**Usage Go**

```go

package main

import (
	"bytes"
	"fmt"
	"io"
	"mime/multipart"
	"net/http"
	"os"
)

func main() {
	file, _ := os.Open("example.mp4")
	defer file.Close()

	body := &bytes.Buffer{}
	writer := multipart.NewWriter(body)
	writer.WriteField("apikey", "your_api_key")
	part, _ := writer.CreateFormFile("file", "example.mp4")
	io.Copy(part, file)
	writer.Close()

	req, _ := http.NewRequest("POST", "https://discardapi.dpdns.org/api/catbox", body)
	req.Header.Set("Content-Type", writer.FormDataContentType())

	client := &http.Client{}
	resp, _ := client.Do(req)
	defer resp.Body.Close()

	buf := new(bytes.Buffer)
	buf.ReadFrom(resp.Body)
	fmt.Println(buf.String())
}
```

**Usage Java**

```java

import okhttp3.*;

import java.io.File;
import java.io.IOException;

public class Upload {
    public static void main(String[] args) throws IOException {
        OkHttpClient client = new OkHttpClient();

        File file = new File("example.mp3");

        RequestBody body = new MultipartBody.Builder()
                .setType(MultipartBody.FORM)
                .addFormDataPart("apikey", "your_api_key")
                .addFormDataPart("file", file.getName(),
                        RequestBody.create(file, MediaType.parse("application/octet-stream")))
                .build();

        Request request = new Request.Builder()
                .url("https://discardapi.dpdns.org/api/catbox")
                .post(body)
                .build();

        Response response = client.newCall(request).execute();
        System.out.println(response.body().string());
    }
}
```

**Usage C#**

```csharp

using System;
using System.Net.Http;
using System.Threading.Tasks;

class Program {
    static async Task Main() {
        var client = new HttpClient();
        var form = new MultipartFormDataContent();
        form.Add(new StringContent("your_api_key"), "apikey");
        form.Add(new StreamContent(System.IO.File.OpenRead("example.txt")), "file", "example.txt");

        var res = await client.PostAsync("https://discardapi.dpdns.org/api/catbox", form);
        var response = await res.Content.ReadAsStringAsync();
        Console.WriteLine(response);
    }
}
```

**Usage Swift**

```swift

import Foundation

let url = URL(string: "https://discardapi.dpdns.org/api/catbox")!
var request = URLRequest(url: url)
request.httpMethod = "POST"

let boundary = UUID().uuidString
request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

var body = Data()
body.append("--\(boundary)\r\n".data(using: .utf8)!)
body.append("Content-Disposition: form-data; name=\"apikey\"\r\n\r\n".data(using: .utf8)!)
body.append("your_api_key\r\n".data(using: .utf8)!)

let fileURL = URL(fileURLWithPath: "example.mov")
let fileData = try Data(contentsOf: fileURL)

body.append("--\(boundary)\r\n".data(using: .utf8)!)
body.append("Content-Disposition: form-data; name=\"file\"; filename=\"example.mov\"\r\n".data(using: .utf8)!)
body.append("Content-Type: application/octet-stream\r\n\r\n".data(using: .utf8)!)
body.append(fileData)
body.append("\r\n".data(using: .utf8)!)
body.append("--\(boundary)--\r\n".data(using: .utf8)!)

request.httpBody = body

URLSession.shared.dataTask(with: request) { data, _, _ in
    if let data = data {
        print(String(data: data, encoding: .utf8)!)
    }
}.resume()
```

**Usage Kotlin**

```kotlin
import okhttp3.*
import java.io.File

fun main() {
    val client = OkHttpClient()
    val file = File("example.apk")

    val body = MultipartBody.Builder()
        .setType(MultipartBody.FORM)
        .addFormDataPart("apikey", "your_api_key")
        .addFormDataPart("file", file.name,
            file.asRequestBody("application/octet-stream".toMediaType()))
        .build()

    val request = Request.Builder()
        .url("https://discardapi.dpdns.org/api/catbox")
        .post(body)
        .build()

    client.newCall(request).execute().use { response ->
        println(response.body?.string())
    }
}
```
---
  
### 🚨 Common Error Codes

- ![](https://img.shields.io/badge/401-red) Please provide the apikey or Invalid apikey  
- ![](https://img.shields.io/badge/403-orange) This endpoint requires Special API key  
- ![](https://img.shields.io/badge/400-orange) Please provide the (query) e.g url  
- ![](https://img.shields.io/badge/429-yellow) Rate limit exceeded, please wait until reset



### 🚨 Error Handling

Comprehensive error codes with detailed descriptions and resolution steps.  
All errors include helpful context and suggestions.  

---

#### 🔑 Authentication Errors  

- ![](https://img.shields.io/badge/401-red) **notparam** → API key parameter missing  
  ➝ Add `?apikey=YOUR_KEY` to your request  

- ![](https://img.shields.io/badge/401-orange) **invalidKey** → Invalid API key provided  
  ➝ Check your key or generate a new one  

- ![](https://img.shields.io/badge/400-orange) **notquery** → Missing required query parameter  
  ➝ Please provide query (e.g. `url`)  

- ![](https://img.shields.io/badge/403-purple) **notspecial** → Requires premium API key  
  ➝ Upgrade your account for access  

---

#### ⏳ Rate Limiting & System  

- ![](https://img.shields.io/badge/429-yellow) **limit** → Rate limit exceeded  
  ➝ Wait for reset or upgrade plan  

- ![](https://img.shields.io/badge/500-gray) **internal** → Internal server error  
  ➝ Temporary issue, try again later  

- ![](https://img.shields.io/badge/404-blue) **notfound** → Endpoint or resource not found  
  ➝ Check the URL and parameters  

---

#### 💡 Best Practices  

- ✅ Always check the `status` field before processing results  
- ✅ Implement exponential backoff for **rate limit** errors  
- ✅ Log error codes for debugging & monitoring  
- ✅ Handle network timeouts gracefully



## 🎧 Support & Contact

Need help or want to upgrade? Our team is here to assist you with integration, troubleshooting, and custom solutions.

### 📞 Contact Methods

- ![](https://img.shields.io/badge/Email-blue) **Email Support** → [discardapi@gmail.com](mailto:discardapi@gmail.com?subject=Support&body=Hello%20Team,)  
- ![](https://img.shields.io/badge/WhatsApp-green) **Live Chat** → [Chat on WhatsApp](https://wa.me/923051391007?text=Hello%20I%20need%20support)  
- ![](https://img.shields.io/badge/Discord-purple) **Community Support** → [Join our Discord Server](https://discord.gg/YBkzCWqz)  
- ![](https://img.shields.io/badge/GitHub-black) **Documentation** → [GitHub Examples](https://github.com/GlobalTechInfo/discard-api)  

---

### ⏱ Response Times
- ✅ **Premium Support** → < 1 hour  
- 🆓 **Free Support** → < 24 hours  

---
© 2025 **Discard API** — Built with Go & Fiber  
