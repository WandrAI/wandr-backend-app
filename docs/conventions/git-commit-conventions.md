# Git Commit Conventions

This document outlines the Git commit message conventions for the Wandr travel app to ensure clear, searchable, and maintainable version history.

## 🎯 Commit Message Format

We follow **Conventional Commits** specification with meaningful one-liners and detailed bodies:

```
<type>(<scope>): <description>

<body>

<footer>
```

### Format Rules

1. **Header**: `<type>(<scope>): <description>` (max 72 characters)
   - **One-liner**: Meaningful summary that stands alone
   - **Imperative mood**: "Add feature" not "Added feature"
   - **No period**: Don't end with punctuation

2. **Body**: Detailed explanation separated by blank line
   - **Why**: Explain the reasoning behind the change
   - **What**: Describe what changed in detail
   - **How**: Include implementation notes if complex
   - **Travel context**: Mention travel app specific implications

3. **Footer**: Breaking changes, issue references (optional)

## 📝 Commit Types

### Primary Types
- **feat**: New feature for travel users
- **fix**: Bug fix that affects travel functionality
- **docs**: Documentation updates (README, ADRs, guides)
- **style**: Code formatting, no logic changes
- **refactor**: Code restructuring without feature changes
- **test**: Adding or modifying tests
- **chore**: Build tools, dependencies, configuration

### Travel App Specific Types
- **travel**: Travel-specific feature implementations
- **ui**: UI/UX improvements for travel interface
- **perf**: Performance improvements for travel scenarios

## 🎨 Scope Examples

### Component Scopes
- **atoms**: Atomic design components (buttons, text, views)
- **molecules**: Molecular components (search bars, cards)
- **organisms**: Complex components (trip planners, maps)
- **templates**: Page-level layouts

### Feature Scopes
- **auth**: Authentication and user management
- **planning**: Trip planning and itinerary features
- **social**: Group collaboration and sharing
- **ai**: AI assistant and recommendations
- **offline**: Offline functionality
- **maps**: Location and mapping features

### Infrastructure Scopes
- **build**: Build system and CI/CD
- **deps**: Dependency management
- **config**: Configuration files
- **docs**: Documentation system

## ✅ Good Commit Examples

### Feature Development
```
feat(planning): add trip sharing functionality

- Implement group trip creation with invitation system
- Add real-time collaboration for itinerary editing
- Include permission levels (view, edit, admin)
- Support for email and deep-link invitations
- Travel-specific: Enables social travel planning workflows

Closes #123
```

### Bug Fixes
```
fix(atoms): resolve StyledButton press state on Android

- Fix TouchableOpacity not responding to press events
- Update pressStyle configuration for Tamagui compatibility
- Add proper feedback for travel booking interactions
- Tested on Android API 28, 31, 34

Fixes #456
```

### Documentation
```
docs(adr): add atomic design component structure decision

- Document rationale for atomic design methodology
- Include travel app specific considerations
- Define component hierarchy and folder structure
- Provide implementation timeline and success criteria
- Reference component patterns and testing approaches
```

### Refactoring
```
refactor(components): migrate to consistent folder structure

- Move all atomic components to folder-based organization
- Update exports and imports throughout codebase
- Maintain backward compatibility during transition
- Co-locate tests with components for better DX
- Prepare foundation for molecule/organism development
```

## ❌ Avoid These Patterns

### Poor Examples
```
# Too vague
git commit -m "fix bug"

# Past tense
git commit -m "Added new feature"

# No context
git commit -m "Update component"

# Too long header
git commit -m "feat(planning): implement comprehensive trip planning system with collaborative editing, real-time updates, and advanced AI recommendations"
```

### Better Alternatives
```
# Specific and clear
fix(atoms): resolve button accessibility on iOS

# Present tense, imperative
feat(planning): add collaborative trip editor

# Proper context
refactor(atoms): standardize component folder structure

# Concise header with details in body
feat(planning): add AI-powered trip recommendations

Implement machine learning-based destination suggestions
- Analyze user preferences and travel history
- Integration with external travel APIs
- Real-time recommendation updates
- Support for group preference aggregation
```

## 🔍 Commit Message Guidelines

### Header Guidelines
1. **Be specific**: "fix login issue" → "fix(auth): resolve OAuth callback handling"
2. **Travel context**: Include travel-relevant implications
3. **Action-oriented**: Start with active verbs
4. **Searchable**: Use consistent terminology

### Body Guidelines
1. **Explain the why**: Motivation for the change
2. **Detail the what**: Specific changes made
3. **Travel implications**: How it affects travel user experience
4. **Technical notes**: Implementation details if complex
5. **Testing notes**: How the change was verified

### Footer Guidelines
1. **Breaking changes**: `BREAKING CHANGE: ...`
2. **Issue references**: `Closes #123`, `Fixes #456`
3. **Co-authors**: `Co-authored-by: Name <email>`

## 🛠️ Tools and Automation

### Recommended Tools
- **Commitizen**: Interactive commit message creation
- **Conventional Changelog**: Automated changelog generation
- **Git hooks**: Validate commit message format

### IDE Integration
- **VSCode**: Git commit message templates
- **Cursor**: Consistent commit patterns

## 📚 Travel App Specific Considerations

### Travel User Stories
When committing travel features, include user story context:
```
feat(social): add group expense splitting

Implement automatic expense tracking and splitting for group trips
- Real-time expense entry during travel
- Automatic currency conversion support
- Fair split algorithms for shared activities
- Integration with popular payment platforms
- Offline-first design for international travel

Enables seamless group travel financial management
```

### Performance Implications
Highlight travel-specific performance considerations:
```
perf(offline): optimize map data caching

- Reduce map tile storage by 60%
- Implement intelligent cache eviction
- Improve offline map loading speed
- Critical for travel scenarios with poor connectivity
- Tested across major travel destinations
```

## 🎯 Benefits

### For Developers
- **Clear history**: Easy to understand code evolution
- **Better debugging**: Link changes to specific issues
- **Code reviews**: Understand change motivation
- **Onboarding**: New developers understand project patterns

### For Travel App
- **Feature tracking**: Monitor travel feature development
- **Release notes**: Generate user-facing changelogs
- **Bug tracking**: Connect fixes to specific travel scenarios
- **Planning**: Understand development velocity and patterns

---

**Last Updated**: June 2025

This convention ensures our Git history tells the story of building a world-class travel app while maintaining professional development standards. When in doubt, prioritize clarity and travel user context in commit messages. 