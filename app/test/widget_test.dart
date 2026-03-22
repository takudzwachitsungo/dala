import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:app/src/app.dart';
import 'package:app/src/app_controller.dart';

void main() {
  testWidgets('shows the Dala welcome flow', (WidgetTester tester) async {
    SharedPreferences.setMockInitialValues(<String, Object>{});

    await tester.pumpWidget(DalaApp(controller: DalaAppController()));
    await tester.pumpAndSettle();

    expect(find.text('Welcome to Dala'), findsOneWidget);
    expect(find.text('Continue anonymously'), findsOneWidget);
  });
}
