import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:frontend/main.dart';

void main() {
  testWidgets('Email Validator UI smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const MyApp());

    // Verify that the AppBar title is displayed.
    expect(find.text('Email Quality Inspector'), findsOneWidget);

    // Verify that the search card header and input field are displayed.
    expect(find.text('Verify Single Recipient'), findsOneWidget);
    expect(find.byType(TextField), findsOneWidget);

    // Verify the Inspect action button is present.
    expect(find.text('Inspect'), findsOneWidget);

    // Enter an email into the text field.
    await tester.enterText(find.byType(TextField), 'test@example.com');
    await tester.pump();

    // Verify the text field now contains the entered email.
    expect(find.text('test@example.com'), findsOneWidget);
  });
}
