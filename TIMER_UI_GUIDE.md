# ⏱️ Timer & Countdown UI Features

## Overview
Complete countdown timer system for OTP verification and rate limiting with user-friendly feedback.

---

## 📋 Features Implemented

### 1. **OTP Validity Timer** (10 minutes)
**Location**: All 3 OTP verification pages
- Shows real-time countdown of OTP validity (10:00 → 0:00)
- Color-coded display:
  - 🟢 **Green** (>2 min): OTP is valid
  - 🟠 **Orange** (1-2 min): OTP expiring soon
  - 🔴 **Red** (<1 min): OTP almost expired
- Auto-notification when OTP expires
- User is prompted to request new OTP

### 2. **Resend OTP Cooldown** (60 seconds)
**Location**: All 3 OTP verification pages
- "Request New OTP" button disabled for 60 seconds after clicking
- Shows countdown: "⏱️ Wait 1:00" (decrements each second)
- Button re-enables automatically after cooldown
- Prevents spam/brute force on OTP endpoint

### 3. **Rate Limit Error Page** (Configurable duration)
**Location**: `errors/429.html`
- Shows when user exceeds rate limit attempts
- Large countdown timer showing retry-after period
- Visual design:
  - Shield icon with danger styling
  - "Too Many Attempts" heading
  - Main timer display (MM:SS format)
  - Tips section with helpful information
  - "Go Back to Home" button
- Auto-redirects when timer expires

### 4. **Smart Timer Logic**
**File**: `static/js/timer.js` (280+ lines)

#### CountdownTimer Class
```javascript
const timer = new CountdownTimer('elementId', durationSeconds, onComplete);
timer.start();
```
- Accurate countdown using `Date.now()`
- Updates every second
- Color changes based on remaining time
- Callback function when timer expires
- Can reset duration mid-countdown

#### ResendOtpButton Class
```javascript
const resendBtn = new ResendOtpButton('buttonId', cooldownSeconds);
resendBtn.setCooldown();
```
- Disables button with visual feedback
- Shows countdown text
- Re-enables when cooldown expires
- Original button text restored

#### RateLimitHandler Class
```javascript
const handler = new RateLimitHandler('containerId');
handler.show(retryAfterSeconds);
```
- Creates or updates rate limit message
- Shows large countdown timer
- Auto-hides when timer expires
- Can be called programmatically

---

## 🎨 UI Components

### OTP Page Timer Display
```html
<div class="alert alert-warning mb-4">
    <i class="fas fa-hourglass-half me-2"></i>
    <span>OTP expires in: <strong id="otpTimer">10:00</strong></span>
</div>
```
- Prominent placement above form
- Icon with clear messaging
- Real-time countdown

### Resend Button with Cooldown
```html
<a href="#" id="resendBtn" class="btn btn-outline-secondary">
    <i class="fas fa-redo"></i> Request New OTP
</a>
<div id="resendCooldown" style="display: none;">
    <small class="text-danger">
        <i class="fas fa-clock"></i> 
        <span id="resendTimer">60</span>s before resend
    </small>
</div>
```
- Button hides, cooldown shows
- Smooth transitions
- Clear indication of wait time

### Rate Limit Error Page
```html
<!-- Large Timer Display -->
<div style="font-size: 2rem; font-weight: bold;" id="retryTimer">
    15:00
</div>

<!-- Tips Section -->
<div class="alert alert-warning">
    <strong>Tips:</strong>
    <ul>
        <li>Make sure you're entering the correct credentials</li>
        <li>Check your email for OTP codes</li>
        <li>If you're locked out, contact support</li>
    </ul>
</div>
```

---

## 🔧 Integration Points

### JavaScript Library Loading
All OTP templates include:
```html
{% load static %}
<script src="{% static 'js/timer.js' %}"></script>
```

### Automatic Initialization
```javascript
document.addEventListener('DOMContentLoaded', function() {
    const otpTimer = new CountdownTimer('otpTimer', 600);
    otpTimer.start();
});
```

### Middleware Integration
Rate limit responses now use:
```python
def rate_limit_response(self, request, message, retry_after=900):
    context = {
        'message': message,
        'retry_after': retry_after,
        'redirect_url': request.META.get('HTTP_REFERER', '/'),
    }
    response = render(request, 'errors/429.html', context, status=429)
    response['Retry-After'] = str(retry_after)  # HTTP standard header
    return response
```

---

## 📱 Responsive Design

All timers are:
- ✅ Mobile-friendly
- ✅ Responsive text sizing
- ✅ Touch-friendly buttons
- ✅ Accessible with icons + text
- ✅ Works in all modern browsers

---

## ⚙️ Configuration

### OTP Timer Duration (Hardcoded - Matches Backend)
```javascript
const otpTimer = new CountdownTimer('otpTimer', 600);  // 10 minutes
```
Matches Django's OTP validity window.

### Resend Cooldown Duration (Hardcoded)
```javascript
let remaining = 60;  // 60 seconds
```
Standard 1-minute cooldown to prevent spam.

### Rate Limit Duration (Dynamic - From Backend)
```python
retry_after = 900  # Default 15 minutes for login
```
Configurable per endpoint via environment variables.

---

## 🔄 User Experience Flow

### OTP Verification Flow
```
1. User navigates to OTP verification page
2. Timer shows "10:00" (green) - OTP is valid
3. User enters OTP code
4. If wrong, can resend after 60s countdown
5. After 10 minutes, timer goes to "0:00" (red)
6. System shows: "OTP has expired"
7. User must request new OTP
```

### Rate Limit Flow
```
1. User attempts login 5 times (limit)
2. Rate limit middleware intercepts 6th attempt
3. User sees 429 error page with "15:00" timer
4. Timer counts down in real-time
5. After 15 minutes, timer reaches "0:00"
6. Page auto-redirects to previous page
7. User can try again
```

---

## 📊 Files Created/Modified

| File | Type | Changes |
|------|------|---------|
| `static/js/timer.js` | NEW | 280+ lines - Timer utilities |
| `core/templates/errors/429.html` | NEW | Rate limit error page |
| `core/templates/core/register_step2_verify_otp.html` | MODIFIED | Added timer & resend |
| `core/templates/core/hr_register_step2_verify_otp.html` | MODIFIED | Added timer & resend |
| `core/templates/core/password_reset_verify_otp.html` | MODIFIED | Added timer & resend |
| `core/middleware.py` | MODIFIED | Return HTML instead of plain text |

---

## 🧪 Testing

### Test OTP Timer
1. Navigate to OTP verification page
2. Verify timer shows "10:00" in orange color
3. Wait 10 seconds, timer should show "9:50"
4. Color should change as time decreases

### Test Resend Cooldown
1. Click "Request New OTP"
2. Button should hide, cooldown shows "60s"
3. Wait 5 seconds, should show "55s"
4. After 60s, button should reappear

### Test Rate Limiting (When Enabled)
1. Set rate limiting env vars to enable
2. Make 5 login attempts (or configured limit)
3. 6th attempt shows 429 page with timer
4. Timer counts down (15 minutes or configured)
5. Page auto-redirects after timer expires

---

## 🔒 Security Features

✅ **Rate Limit Protection**: Prevents brute force attacks
✅ **OTP Timeout**: OTP validity expires after 10 minutes
✅ **Resend Cooldown**: Prevents OTP spam
✅ **User Feedback**: Clear messaging about restrictions
✅ **HTTP Standard**: Uses Retry-After header
✅ **Client-Side Validation**: Disables buttons immediately

---

## 📝 Implementation Notes

- **Browser Compatibility**: All modern browsers (Chrome, Firefox, Safari, Edge)
- **No Dependencies**: Pure JavaScript, no jQuery or other libraries
- **Accessibility**: Uses ARIA labels and semantic HTML
- **Performance**: Minimal DOM updates (only timer text changes)
- **Offline**: Timers work without server synchronization

---

## 🚀 Production Ready

✅ Tested on local development
✅ Deployed to Render (commit: d2eb48f)
✅ All rate limiting endpoints protected
✅ User-friendly error messages
✅ Automatic redirect on 429 timeout

Users will now see clear countdown timers and helpful feedback when interacting with rate-limited endpoints or OTP verification!
