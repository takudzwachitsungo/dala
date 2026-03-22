import 'package:flutter/material.dart';

import '../app_controller.dart';
import 'circles_page.dart';
import 'companion_page.dart';
import 'home_page.dart';
import 'paths_page.dart';
import 'profile_page.dart';

class DalaShellPage extends StatelessWidget {
  const DalaShellPage({super.key, required this.controller});

  final DalaAppController controller;

  @override
  Widget build(BuildContext context) {
    final pages = [
      HomePage(controller: controller),
      CompanionPage(controller: controller),
      PathsPage(controller: controller),
      CirclesPage(controller: controller),
      ProfilePage(controller: controller),
    ];

    return Scaffold(
      body: IndexedStack(index: controller.selectedTab.index, children: pages),
      bottomNavigationBar: NavigationBar(
        selectedIndex: controller.selectedTab.index,
        onDestinationSelected: (index) {
          controller.selectTab(AppTab.values[index]);
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.home_outlined),
            selectedIcon: Icon(Icons.home_rounded),
            label: 'Home',
          ),
          NavigationDestination(
            icon: Icon(Icons.chat_bubble_outline_rounded),
            selectedIcon: Icon(Icons.chat_bubble_rounded),
            label: 'Companion',
          ),
          NavigationDestination(
            icon: Icon(Icons.explore_outlined),
            selectedIcon: Icon(Icons.explore_rounded),
            label: 'Paths',
          ),
          NavigationDestination(
            icon: Icon(Icons.groups_outlined),
            selectedIcon: Icon(Icons.groups_rounded),
            label: 'Circles',
          ),
          NavigationDestination(
            icon: Icon(Icons.person_outline_rounded),
            selectedIcon: Icon(Icons.person_rounded),
            label: 'Profile',
          ),
        ],
      ),
    );
  }
}
