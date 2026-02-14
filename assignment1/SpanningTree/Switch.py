"""
/*
 * Copyright © 2022 Georgia Institute of Technology (Georgia Tech). All Rights Reserved.
 * Template code for CS 6250 Computer Networks
 * Instructors: Maria Konte
 * Head TAs: Johann Lau and Ken Westdorp
 *
 * Georgia Tech asserts copyright ownership of this template and all derivative
 * works, including solutions to the projects assigned in this course. Students
 * and other users of this template code are advised not to share it with others
 * or to make it available on publicly viewable websites including repositories
 * such as GitHub and GitLab. This copyright statement should not be removed
 * or edited. Removing it will be considered an academic integrity issue.
 *
 * We do grant permission to share solutions privately with non-students such
 * as potential employers as long as this header remains in full. However,
 * sharing with other current or future students or using a medium to share
 * where the code is widely available on the internet is prohibited and
 * subject to being investigated as a GT honor code violation.
 * Please respect the intellectual ownership of the course materials
 * (including exam keys, project requirements, etc.) and do not distribute them
 * to anyone not enrolled in the class. Use of any previous semester course
 * materials, such as tests, quizzes, homework, projects, videos, and any other
 * coursework, is prohibited in this course.
 */
"""

# Spanning Tree Protocol project for GA Tech OMSCS CS-6250: Computer Networks
#
# Copyright 2023 Vincent Hu
#           Based on prior work by Sean Donovan, Jared Scott, James Lohse, and Michael Brown

from Message import Message
from StpSwitch import StpSwitch


class Switch(StpSwitch):
    """
    This class defines a Switch (node/bridge) that can send and receive messages
    to converge on a final, loop-free spanning tree. This class
    is a child class of the StpSwitch class. To remain within the spirit of
    the project, the only inherited members or functions a student is permitted
    to use are:

    switchID: int
        the ID number of this switch object
    links: list
        the list of switch IDs connected to this switch object)
    send_message(msg: Message)
        Sends a Message object to another switch)

    Students should use the send_message function to implement the algorithm.
    Do NOT use the self.topology.send_message function. A non-distributed (centralized)
    algorithm will not receive credit. Do NOT use global variables.

    Student code should NOT access the following members, otherwise they may violate
    the spirit of the project:

    topolink: Topology
        a link to the greater Topology structure used for message passing
    self.topology: Topology
        a link to the greater Topology structure used for message passing
    """

    def __init__(self, switchID: int, topolink: object, links: list):
        """
        Invokes the super class constructor (StpSwitch), which makes the following
        members available to this object:

        switchID: int
            the ID number of this switch object
        links: list
            the list of switch IDs connected to this switch object
        """
        super(Switch, self).__init__(switchID, topolink, links)
        # TODO: Define instance members to keep track of which links are part of the spanning tree
        self.root_id = self.switchID
        self.distance_to_root = 0
        self.active_links = set()
        self.path_to_root = None

    def process_message(self, message: Message):
        """
        Processes the messages from other switches. Updates its own data (members),
        if necessary, and sends messages to its neighbors, as needed.

        message: Message
            the Message received from other Switches
        """
        # TODO: This function needs to accept an incoming message and process it accordingly.
        #      This function is called every time the switch receives a new message.

        message.ttl = max(0, message.ttl - 1)

        updated = False
        old_path = self.path_to_root

        candidate_root = message.root
        candidate_dist = message.distance + 1
        candidate_next = message.origin

        if candidate_root < self.root_id:
            self.root_id = candidate_root
            self.distance_to_root = candidate_dist
            self.path_to_root = candidate_next
            updated = True
        elif candidate_root == self.root_id:
            if candidate_dist < self.distance_to_root:
                self.distance_to_root = candidate_dist
                self.path_to_root = candidate_next
                updated = True
            elif candidate_dist == self.distance_to_root:
                if self.path_to_root is None or candidate_next < self.path_to_root:
                    self.path_to_root = candidate_next
                    updated = True

        if old_path != self.path_to_root:
            if old_path is not None:
                self.active_links.discard(old_path)
            if self.path_to_root is not None:
                self.active_links.add(self.path_to_root)

        if message.pathThrough:
            self.active_links.add(message.origin)
        else:
            if message.origin != self.path_to_root:
                self.active_links.discard(message.origin)

        if self.root_id == self.switchID:
            if self.path_to_root is not None or self.distance_to_root != 0:
                updated = True
            self.distance_to_root = 0
            if self.path_to_root is not None:
                self.active_links.discard(self.path_to_root)
            self.path_to_root = None

        if updated or message.ttl > 0:
            for neighbor_id in self.links:
                path_through = (self.path_to_root is not None and neighbor_id == self.path_to_root)
                msg = Message(self.root_id, self.distance_to_root, self.switchID,
                              neighbor_id, path_through, message.ttl)
                self.send_message(msg)


    def generate_logstring(self):
        """
        Logs this Switch's list of Active Links in a SORTED order

        returns a String of format:
            SwitchID - ActiveLink1, SwitchID - ActiveLink2, etc.
        """
        # TODO: This function needs to return a logstring for this particular switch.  The
        #      string represents the active forwarding links for this switch and is invoked
        #      only after the simulation is complete.  Output the links included in the
        #      spanning tree by INCREASING destination switch ID on a single line.
        #
        #      Print links as '(source switch id) - (destination switch id)', separating links
        #      with a comma - ','.
        #
        #      For example, given a spanning tree (1 ----- 2 ----- 3), a correct output string
        #      for switch 2 would have the following text:
        #      2 - 1, 2 - 3
        #
        #      A full example of a valid output file is included (Logs/) in the project skeleton.
        if not self.active_links:
            return ""
        sorted_links = sorted(self.active_links)
        log_list = [f"{self.switchID} - {link}" for link in sorted_links]
        return ", ".join(log_list)