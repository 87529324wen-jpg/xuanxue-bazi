# macOS Vision OCR (PyObjC)

When tesseract/brew unavailable, use macOS built-in Vision framework for Chinese+English OCR.

## Working Code (verified 2026-05-06)
```python
import objc
from Foundation import NSURL
import Quartz
from Vision import VNImageRequestHandler, VNRecognizeTextRequest

def ocr_image(path):
    url = NSURL.fileURLWithPath_(path)
    source = Quartz.CGImageSourceCreateWithURL(url, None)
    cg_image = Quartz.CGImageSourceCreateImageAtIndex(source, 0, None)
    handler = VNImageRequestHandler.alloc().initWithCGImage_options_(cg_image, None)
    results = []
    def handler_fn(request, error):
        for obs in request.results():
            results.append(obs.topCandidates_(1)[0].string())
    request = VNRecognizeTextRequest.alloc().initWithCompletionHandler_(handler_fn)
    request.setRecognitionLanguages_(["zh-Hans", "en"])
    request.setRecognitionLevel_(0)  # 0=accurate, 1=fast
    handler.performRequests_error_([request], None)
    return "\n".join(results)
```

## Key Pitfalls
- Method name is `.string()` NOT `.string_()` or `.stringValue()` (verified by dir() inspection)
- Works with JPG, PNG via CGImageSourceCreateWithURL
- Quality depends on image resolution
