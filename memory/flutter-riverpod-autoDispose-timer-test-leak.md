# Flutter Riverpod autoDispose + periodic Timer leaks into fake-async tests

## Symptom
Widget tests fail with:
```
A Timer is still pending even after the widget tree was disposed.
'package:flutter_test/src/binding.dart':
Failed assertion: line 2543 pos 12: '!timersPending'
```
The Timer is `Timer.periodic(...)` started inside a `Notifier.build()`.

## Root cause
1. `Notifier.build()` starts a `Timer.periodic(probeInterval, ...)`.
2. Tests use `flutter_test`, which wraps everything in a fake-async zone.
3. The timer schedules a `FakeTimer` in that zone. After `pumpAndSettle()`,
   the timer is still pending.
4. `flutter_test` checks for pending timers in `_verifyInvariants` BEFORE
   widget teardown (test framework order is fixed).
5. Result: assertion failure.

`ref.onDispose` *does* cancel the timer — but only during widget teardown,
which runs after `_verifyInvariants`.

## Fix (in order of preference)
1. **Stub the notifier in tests that don't care about the timer.** Most
   tests for the AppShell don't care that connectivity is being polled;
   they care that the rail/nav renders. Override the provider with a
   `_NoopNotifier extends TheNotifier { @override build() => initialState; }`
   that starts no timer. This is the cleanest pattern — production code
   runs the timer, test code skips it.
2. **Use `NotifierProvider.autoDispose`** (Riverpod 3) so the timer
   cancels the moment no widget watches the provider. Still leaks into
   `_verifyInvariants` if anything briefly subscribes during the test.
3. **Use `Future.delayed` chained manually** instead of `Timer.periodic`.
   Cancel each chain in `onDispose`. More code, same leak risk.

## Verification
After fix: `flutter test` green, `flutter analyze` clean, `make check`
passes.
