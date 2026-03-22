import 'package:flutter/material.dart';

import '../app_controller.dart';
import '../theme/app_theme.dart';
import '../widgets/dala_scaffold.dart';

enum _AuthFlowMode { signUp, login }

class WelcomePage extends StatelessWidget {
  const WelcomePage({super.key, required this.controller});

  final DalaAppController controller;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      body: DalaScaffold(
        child: CustomScrollView(
          slivers: [
            SliverFillRemaining(
              hasScrollBody: false,
              child: Padding(
                padding: const EdgeInsets.symmetric(
                  horizontal: 24,
                  vertical: 40,
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const Spacer(),
                    Center(
                      child: Text(
                        'Dala',
                        style: Theme.of(context).textTheme.displaySmall
                            ?.copyWith(
                              color: AppTheme.primaryText,
                              fontWeight: FontWeight.w300,
                              letterSpacing: -0.5,
                            ),
                      ),
                    ),
                    const SizedBox(height: 48),
                    Container(
                      padding: const EdgeInsets.all(32),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(24),
                        boxShadow: const [
                          BoxShadow(
                            color: Color(0x08000000),
                            blurRadius: 20,
                            offset: Offset(0, 4),
                          ),
                        ],
                      ),
                      child: AnimatedBuilder(
                        animation: controller,
                        builder: (context, _) {
                          return Column(
                            crossAxisAlignment: CrossAxisAlignment.center,
                            children: [
                              Text(
                                'Welcome to Dala',
                                style: Theme.of(context).textTheme.headlineSmall
                                    ?.copyWith(
                                      color: AppTheme.primaryText,
                                      fontWeight: FontWeight.w400,
                                    ),
                              ),
                              const SizedBox(height: 12),
                              Text(
                                'A safe place to pause and feel heard.',
                                textAlign: TextAlign.center,
                                style: Theme.of(context).textTheme.bodyLarge
                                    ?.copyWith(color: AppTheme.secondaryText),
                              ),
                              const SizedBox(height: 32),
                              SizedBox(
                                width: double.infinity,
                                child: FilledButton.icon(
                                  onPressed: controller.isCreatingSession
                                      ? null
                                      : () => controller.continueAnonymously(),
                                  iconAlignment: IconAlignment.end,
                                  icon: const Icon(
                                    Icons.arrow_forward_rounded,
                                    size: 20,
                                  ),
                                  label: Text(
                                    controller.isCreatingSession
                                        ? 'Creating account...'
                                        : 'Continue Anonymously',
                                    style: const TextStyle(
                                      fontWeight: FontWeight.w600,
                                      fontSize: 16,
                                    ),
                                  ),
                                ),
                              ),
                              const SizedBox(height: 32),
                              Row(
                                children: [
                                  const Expanded(
                                    child: Divider(color: AppTheme.dividerBg),
                                  ),
                                  Padding(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 16,
                                    ),
                                    child: Text(
                                      'OR USE AN ACCOUNT',
                                      style: Theme.of(context)
                                          .textTheme
                                          .labelSmall
                                          ?.copyWith(
                                            color: AppTheme.subtle,
                                            letterSpacing: 0.5,
                                          ),
                                    ),
                                  ),
                                  const Expanded(
                                    child: Divider(color: AppTheme.dividerBg),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 32),
                              SizedBox(
                                width: double.infinity,
                                child: OutlinedButton(
                                  onPressed: () => _openAuthPage(
                                    context,
                                    _AuthFlowMode.signUp,
                                  ),
                                  style: OutlinedButton.styleFrom(
                                    side: const BorderSide(
                                      color: AppTheme.dividerBg,
                                    ),
                                  ),
                                  child: const Text('Sign Up'),
                                ),
                              ),
                              const SizedBox(height: 24),
                              GestureDetector(
                                onTap: () =>
                                    _openAuthPage(context, _AuthFlowMode.login),
                                child: RichText(
                                  textAlign: TextAlign.center,
                                  text: TextSpan(
                                    text: 'Already have an account? ',
                                    style: Theme.of(context)
                                        .textTheme
                                        .bodyMedium
                                        ?.copyWith(
                                          color: AppTheme.secondaryText,
                                        ),
                                    children: const [
                                      TextSpan(
                                        text: 'Log In',
                                        style: TextStyle(
                                          color: AppTheme.sage,
                                          fontWeight: FontWeight.w600,
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                              if (controller.errorMessage != null) ...[
                                const SizedBox(height: 24),
                                Container(
                                  width: double.infinity,
                                  padding: const EdgeInsets.all(14),
                                  decoration: BoxDecoration(
                                    color: const Color(0xFFF8ECE6),
                                    borderRadius: BorderRadius.circular(18),
                                  ),
                                  child: Text(
                                    controller.errorMessage!,
                                    textAlign: TextAlign.center,
                                    style: Theme.of(context).textTheme.bodySmall
                                        ?.copyWith(
                                          color: AppTheme.primaryText,
                                          height: 1.35,
                                        ),
                                  ),
                                ),
                              ],
                            ],
                          );
                        },
                      ),
                    ),
                    const Spacer(),
                    const SizedBox(height: 40),
                    Center(
                      child: Text(
                        'Private. Non-judgmental. At your pace.',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: AppTheme.subtle,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _openAuthPage(
    BuildContext context,
    _AuthFlowMode initialMode,
  ) async {
    await Navigator.of(context).push(
      MaterialPageRoute<void>(
        builder: (context) =>
            _AuthPage(controller: controller, initialMode: initialMode),
      ),
    );
  }
}

class _AuthPage extends StatefulWidget {
  const _AuthPage({required this.controller, required this.initialMode});

  final DalaAppController controller;
  final _AuthFlowMode initialMode;

  @override
  State<_AuthPage> createState() => _AuthPageState();
}

class _AuthPageState extends State<_AuthPage> {
  final _formKey = GlobalKey<FormState>();
  late _AuthFlowMode _mode;

  final TextEditingController _usernameController = TextEditingController();
  final TextEditingController _emailController = TextEditingController();
  final TextEditingController _identifierController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final TextEditingController _confirmPasswordController =
      TextEditingController();

  @override
  void initState() {
    super.initState();
    _mode = widget.initialMode;
  }

  @override
  void dispose() {
    _usernameController.dispose();
    _emailController.dispose();
    _identifierController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.background,
      appBar: AppBar(
        title: Text(
          _mode == _AuthFlowMode.signUp ? 'Create account' : 'Log in',
        ),
      ),
      body: DalaScaffold(
        child: AnimatedBuilder(
          animation: widget.controller,
          builder: (context, _) {
            final isBusy = widget.controller.isAuthenticating;

            return SafeArea(
              child: SingleChildScrollView(
                padding: const EdgeInsets.fromLTRB(24, 12, 24, 32),
                child: Form(
                  key: _formKey,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      Text(
                        _mode == _AuthFlowMode.signUp
                            ? 'Create a Dala account'
                            : 'Welcome back',
                        style: Theme.of(context).textTheme.headlineSmall
                            ?.copyWith(
                              color: AppTheme.primaryText,
                              fontWeight: FontWeight.w500,
                            ),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        _mode == _AuthFlowMode.signUp
                            ? 'Save your progress across devices and keep your support journey with you.'
                            : 'Use your username or email to continue where you left off.',
                        style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                          color: AppTheme.secondaryText,
                          height: 1.4,
                        ),
                      ),
                      const SizedBox(height: 28),
                      if (_mode == _AuthFlowMode.signUp) ...[
                        TextFormField(
                          controller: _usernameController,
                          textInputAction: TextInputAction.next,
                          decoration: const InputDecoration(
                            labelText: 'Username',
                            hintText: 'Choose a username',
                          ),
                          validator: (value) {
                            final text = value?.trim() ?? '';
                            if (text.length < 3) {
                              return 'Username must be at least 3 characters.';
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 16),
                        TextFormField(
                          controller: _emailController,
                          textInputAction: TextInputAction.next,
                          keyboardType: TextInputType.emailAddress,
                          decoration: const InputDecoration(
                            labelText: 'Email (optional)',
                            hintText: 'you@example.com',
                          ),
                          validator: (value) {
                            final text = value?.trim() ?? '';
                            if (text.isEmpty || text.contains('@')) {
                              return null;
                            }
                            return 'Enter a valid email or leave it blank.';
                          },
                        ),
                        const SizedBox(height: 16),
                      ] else ...[
                        TextFormField(
                          controller: _identifierController,
                          textInputAction: TextInputAction.next,
                          decoration: const InputDecoration(
                            labelText: 'Username or email',
                            hintText: 'Enter your username or email',
                          ),
                          validator: (value) {
                            if ((value?.trim() ?? '').isEmpty) {
                              return 'Enter your username or email.';
                            }
                            return null;
                          },
                        ),
                        const SizedBox(height: 16),
                      ],
                      TextFormField(
                        controller: _passwordController,
                        obscureText: true,
                        textInputAction: _mode == _AuthFlowMode.signUp
                            ? TextInputAction.next
                            : TextInputAction.done,
                        onFieldSubmitted: (_) {
                          if (_mode == _AuthFlowMode.login) {
                            _submit();
                          }
                        },
                        decoration: const InputDecoration(
                          labelText: 'Password',
                          hintText: 'Enter your password',
                        ),
                        validator: (value) {
                          final text = value ?? '';
                          if (text.length < 8) {
                            return 'Password must be at least 8 characters.';
                          }
                          return null;
                        },
                      ),
                      if (_mode == _AuthFlowMode.signUp) ...[
                        const SizedBox(height: 16),
                        TextFormField(
                          controller: _confirmPasswordController,
                          obscureText: true,
                          textInputAction: TextInputAction.done,
                          onFieldSubmitted: (_) => _submit(),
                          decoration: const InputDecoration(
                            labelText: 'Confirm password',
                            hintText: 'Re-enter your password',
                          ),
                          validator: (value) {
                            if (value != _passwordController.text) {
                              return 'Passwords do not match.';
                            }
                            return null;
                          },
                        ),
                      ],
                      if (widget.controller.errorMessage != null) ...[
                        const SizedBox(height: 18),
                        Container(
                          padding: const EdgeInsets.all(14),
                          decoration: BoxDecoration(
                            color: const Color(0xFFF8ECE6),
                            borderRadius: BorderRadius.circular(18),
                          ),
                          child: Text(
                            widget.controller.errorMessage!,
                            style: Theme.of(context).textTheme.bodySmall
                                ?.copyWith(
                                  color: AppTheme.primaryText,
                                  height: 1.35,
                                ),
                          ),
                        ),
                      ],
                      const SizedBox(height: 24),
                      FilledButton(
                        onPressed: isBusy ? null : _submit,
                        child: Text(
                          isBusy
                              ? (_mode == _AuthFlowMode.signUp
                                    ? 'Creating account...'
                                    : 'Logging in...')
                              : (_mode == _AuthFlowMode.signUp
                                    ? 'Create account'
                                    : 'Log in'),
                        ),
                      ),
                      const SizedBox(height: 16),
                      TextButton(
                        onPressed: isBusy
                            ? null
                            : () {
                                setState(() {
                                  _mode = _mode == _AuthFlowMode.signUp
                                      ? _AuthFlowMode.login
                                      : _AuthFlowMode.signUp;
                                });
                              },
                        child: Text(
                          _mode == _AuthFlowMode.signUp
                              ? 'Already have an account? Log in'
                              : 'Need an account? Sign up',
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            );
          },
        ),
      ),
    );
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) {
      return;
    }

    if (_mode == _AuthFlowMode.signUp) {
      await widget.controller.register(
        username: _usernameController.text,
        email: _emailController.text,
        password: _passwordController.text,
      );
    } else {
      await widget.controller.login(
        identifier: _identifierController.text,
        password: _passwordController.text,
      );
    }

    if (!mounted) {
      return;
    }

    if (widget.controller.hasSession) {
      Navigator.of(context).pop();
    }
  }
}
