# Contributing to RecruitHub

Thank you for interest in contributing to RecruitHub! Here are guidelines to help you get started.

## 🎯 How to Contribute

### Reporting Bugs
- Check existing issues first
- Provide clear description of the bug
- Include steps to reproduce
- Share error messages and screenshots
- Mention your environment (OS, Python version, Django version)

### Suggesting Enhancements
- Use GitHub Issues with descriptive title
- Explain the enhancement and use cases
- Include mockups/examples if applicable

### Submitting Pull Requests
1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Make your changes
4. Write clear commit messages
5. Push to your fork: `git push origin feature/my-feature`
6. Submit Pull Request with description

## 📋 Code Standards

### Python Style
- Follow PEP 8 style guide
- Use meaningful variable names
- Add docstrings to functions
- Keep functions focused and small

### Django Conventions
- Place business logic in models
- Keep views simple and focused
- Use Django ORM instead of raw SQL
- Use Django Forms for validation

### Templates
- Use Django template syntax correctly
- Maintain Bootstrap 5.3 consistency
- Include proper accessibility attributes
- Keep CSS/JS within style/script tags

## 🔄 Development Workflow

### Setup Development Environment
```bash
git clone https://github.com/yourusername/RecruitHub.git
cd RecruitHub
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### Commit Best Practices
- Commit small, logical changes
- Use clear commit messages
- Reference issue numbers: "Fixes #123"

### Test Your Changes
- Test on multiple browsers
- Test both student and HR workflows
- Verify database migrations work
- Check for console errors

## 🚀 Feature Development Areas

### High Priority
- Email verification system
- Interview scheduling
- Advanced analytics dashboard
- Batch CSV import

### Medium Priority
- Multi-company support
- Student visibility controls
- Notification system
- Export reports

### Low Priority
- API endpoints
- Mobile app
- AI resume scoring
- Video interview integration

## 📝 Commit Message Format

```
[TYPE] Brief description

Detailed explanation of changes if needed.

Fixes #issue_number (if applicable)
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`

Example:
```
[feat] Add email verification for new student registrations

- Implemented email verification process
- Added email template
- Updated registration flow
- Added tests for email verification

Fixes #42
```

## ✅ Before Submitting PR

- [ ] Code follows style guide
- [ ] Changes tested locally
- [ ] Database migrations work
- [ ] No console errors
- [ ] Updated documentation if needed
- [ ] PR description is clear

## 🤝 Code Review Process

1. Maintainer reviews your PR
2. Feedback provided for improvements
3. Make requested changes
4. PR merged once approved

## 📚 Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django Best Practices](https://docs.djangoproject.com/en/stable/misc/design-philosophies/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)
- [PEP 8 Style Guide](https://pep8.org/)

## 💬 Questions?

- Open a GitHub Discussion
- Ask in Pull Request comments
- Check existing documentation

---

**Thank you for making RecruitHub better! 🙌**
