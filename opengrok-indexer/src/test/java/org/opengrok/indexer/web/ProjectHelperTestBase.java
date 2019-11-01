/*
 * CDDL HEADER START
 *
 * The contents of this file are subject to the terms of the
 * Common Development and Distribution License (the "License").
 * You may not use this file except in compliance with the License.
 *
 * See LICENSE.txt included in this distribution for the specific
 * language governing permissions and limitations under the License.
 *
 * When distributing Covered Code, include this CDDL HEADER in each
 * file and include the License file at LICENSE.txt.
 * If applicable, add the following below this CDDL HEADER, with the
 * fields enclosed by brackets "[]" replaced with your own identifying
 * information: Portions Copyright [yyyy] [name of copyright owner]
 *
 * CDDL HEADER END
 */

/*
 * Copyright (c) 2016, 2018, Oracle and/or its affiliates. All rights reserved.
 */
package org.opengrok.indexer.web;

import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;
import javax.servlet.http.HttpServletRequest;
import org.junit.After;
import org.junit.AfterClass;
import org.junit.Assert;
import org.junit.Before;
import org.junit.BeforeClass;
import org.opengrok.indexer.authorization.AuthorizationFramework;
import org.opengrok.indexer.authorization.IAuthorizationPlugin;
import org.opengrok.indexer.authorization.TestPlugin;
import org.opengrok.indexer.configuration.Group;
import org.opengrok.indexer.configuration.Project;
import org.opengrok.indexer.configuration.RuntimeEnvironment;
import org.opengrok.indexer.history.RepoRepository;
import org.opengrok.indexer.history.RepositoryInfo;

public class ProjectHelperTestBase {

    protected static Set<Group> groups;
    protected static Map<String, Project> projects;
    protected static List<RepositoryInfo> repositories;
    protected static RuntimeEnvironment env;
    protected static Map<Project, List<RepositoryInfo>> repositories_map;

    protected PageConfig cfg;
    protected ProjectHelper helper;

    protected static Project createRepository(
            int index,
            int number,
            int cnt,
            boolean grouped,
            boolean allowed,
            List<RepositoryInfo> rps,
            Map<String, Project> prjs,
            Map<Project, List<RepositoryInfo>> map) {

        Project p = createProject(index, number, grouped, allowed, true, rps, prjs, map);

        for (int i = 0; i < cnt; i++) {
            RepositoryInfo info = new RepoRepository();
            info.setParent(p.getName() + "_" + i);
            info.setDirectoryNameRelative(p.getPath());
            rps.add(info);
            List<RepositoryInfo> infos = map.get(p);
            if (infos == null) {
                infos = new ArrayList<>();
            }
            infos.add(info);
            map.put(p, infos);
        }
        return p;
    }

    protected static Project createProject(
            int index,
            int number,
            boolean grouped,
            boolean allowed,
            boolean repository,
            List<RepositoryInfo> rps,
            Map<String, Project> prjs,
            Map<Project, List<RepositoryInfo>> map) {

        Project p = new Project(
                (allowed ? "allowed_" : "")
                + (grouped ? "grouped_" : "ungrouped_")
                + (repository ? "repository" : "project")
                + "_" + index + "_" + number);
        prjs.put(p.getName(), p);
        p.setIndexed(true);
        return p;
    }

    protected static void createGroups(
            int start,
            int cnt,
            boolean allowed,
            List<RepositoryInfo> rps,
            Map<Project, List<RepositoryInfo>> map,
            Map<String, Project> prjs,
            List<Group> grps) {

        for (int i = start; i < start + cnt; i++) {
            Group g = new Group((allowed ? "allowed_" : "") + "group_" + i);
            String pattern = "";

            pattern += createProject(i, 1, true, false, false, rps, prjs, map).getName() + "|";
            pattern += createProject(i, 2, true, false, false, rps, prjs, map).getName() + "|";

            pattern += createProject(i, 1, true, true, false, rps, prjs, map).getName() + "|";
            pattern += createProject(i, 2, true, true, false, rps, prjs, map).getName() + "|";

            pattern += createRepository(i, 1, 1, true, false, rps, prjs, map).getName() + "|";
            pattern += createRepository(i, 2, 1, true, false, rps, prjs, map).getName() + "|";

            pattern += createRepository(i, 1, 1, true, true, rps, prjs, map).getName() + "|";
            pattern += createRepository(i, 2, 1, true, true, rps, prjs, map).getName();

            g.setPattern(pattern);
            grps.add(g);
        }
    }

    @SuppressWarnings("unchecked")
    protected static Map<Project, List<RepositoryInfo>> getRepositoriesMap() {
        try {
            Field field = RuntimeEnvironment.class.getDeclaredField("repository_map");
            field.setAccessible(true);
            return (Map<Project, List<RepositoryInfo>>) field.get(RuntimeEnvironment.getInstance());
        } catch (Throwable ex) {
            Assert.fail("invoking getRepositoriesMap should not throw an exception");
        }
        return null;
    }

    protected static void setRepositoriesMap(Map<Project, List<RepositoryInfo>> map) {
        try {
            Field field = RuntimeEnvironment.class.getDeclaredField("repository_map");
            field.setAccessible(true);
            field.set(RuntimeEnvironment.getInstance(), map);
        } catch (Throwable ex) {
            Assert.fail("invoking getRepositoriesMap should not throw an exception");
        }
    }

    /**
     * The setup should create a structure like this.
     *
     * <pre>
     * Group: allowed_group_2
     *  projects:
     *      allowed_grouped_project_2_1,allowed_grouped_project_2_2,
     *      grouped_project_2_1,grouped_project_2_2
     *  repositories:
     *      allowed_grouped_repository_2_1,allowed_grouped_repository_2_2,
     *      grouped_repository_2_1,grouped_repository_2_2
     *
     * Group: allowed_group_3
     *  projects:
     *      allowed_grouped_project_3_1,allowed_grouped_project_3_2,
     *      grouped_project_3_1,grouped_project_3_2
     *  repositories:
     *      allowed_grouped_repository_3_1,allowed_grouped_repository_3_2,
     *      grouped_repository_3_1,grouped_repository_3_2
     *
     * Group: group_0
     *  projects:
     *      allowed_grouped_project_0_1,allowed_grouped_project_0_2,
     *      grouped_project_0_1,grouped_project_0_2
     *  repositories:
     *      allowed_grouped_repository_0_1,allowed_grouped_repository_0_2,
     *      grouped_repository_0_1,grouped_repository_0_2
     *
     * Group: group_1
     *  projects:
     *      allowed_grouped_project_1_1,allowed_grouped_project_1_2,
     *      grouped_project_1_1,grouped_project_1_2
     *  repositories:
     *      allowed_grouped_repository_1_1,allowed_grouped_repository_1_2,
     *      grouped_repository_1_1,grouped_repository_1_2
     *
     * ungrouped projects:
     *  ungrouped_project_0_1,ungrouped_project_1_1,
     *  allowed_ungrouped_project_2_1, allowed_ungrouped_project_3_1
     *
     * ungrouped repositories:
     *  ungrouped_repository_0_1, ungrouped_repository_1_1,
     *  allowed_ungrouped_repository_2_1, allowed_ungrouped_repository_3_1
     * </pre>
     */
    @BeforeClass
    public static void setUpClass() {
        env = RuntimeEnvironment.getInstance();
        groups = env.getGroups();
        projects = env.getProjects();
        repositories = env.getRepositories();
        repositories_map = getRepositoriesMap();
        env.setPluginDirectory(null);

        List<Group> grps = new ArrayList<>();
        Map<String, Project> prjs = new HashMap<>();
        List<RepositoryInfo> rps = new ArrayList<>();
        Map<Project, List<RepositoryInfo>> map = new TreeMap<>();

        createGroups(0, 2, false, rps, map, prjs, grps);
        createGroups(2, 2, true, rps, map, prjs, grps);

        for (int i = 0; i < 2; i++) {
            createProject(i, 1, false, false, false, rps, prjs, map);
        }

        for (int i = 0 + 2; i < 2 + 2; i++) {
            createProject(i, 1, false, true, false, rps, prjs, map);
        }

        for (int i = 0; i < 2; i++) {
            createRepository(i, 1, 1, false, false, rps, prjs, map);
        }

        for (int i = 0 + 2; i < 2 + 2; i++) {
            createRepository(i, 1, 1, false, true, rps, prjs, map);
        }

        setRepositoriesMap(map);
        env.setProjects(prjs);
        env.setGroups(new TreeSet<>(grps));
        env.setRepositories(rps);
    }

    @AfterClass
    public static void tearDownClass() {
        setRepositoriesMap(repositories_map);
        env.setProjects(projects);
        env.setGroups(groups);
        env.setRepositories(repositories);
    }

    protected void invokeAddPlugin(IAuthorizationPlugin plugin) {
        env.getAuthorizationFramework().addPlugin(env.getAuthorizationFramework().getStack(), plugin);
    }

    protected HttpServletRequest getRequest() {
        return new DummyHttpServletRequest() {
        };
    }

    @Before
    public void setUp() {
        Assert.assertEquals("Should contain 4 groups", 4, env.getGroups().size());
        Assert.assertEquals("Should contain 40 project", 40, env.getProjects().size());
        Assert.assertEquals("Should contain 20 repositories", 20, env.getRepositories().size());
        Assert.assertNotNull("Repository map should not be null", env.getProjectRepositoriesMap());
        Assert.assertEquals("Repository map should contain 20 project", 20, env.getProjectRepositoriesMap().size());

        env.setAuthorizationFramework(new AuthorizationFramework());
        env.getAuthorizationFramework().reload();

        IAuthorizationPlugin plugin = new TestPlugin() {
            @Override
            public boolean isAllowed(HttpServletRequest request, Project project) {
                return project.getName().startsWith("allowed");
            }

            @Override
            public boolean isAllowed(HttpServletRequest request, Group group) {
                return group.getName().startsWith("allowed");
            }
        };

        invokeAddPlugin(plugin);

        cfg = PageConfig.get(getRequest());
        helper = cfg.getProjectHelper();
    }

    @After
    public void tearDown() {
        env.getAuthorizationFramework().removeAll();
    }
}
