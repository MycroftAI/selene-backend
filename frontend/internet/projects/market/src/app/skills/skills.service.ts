import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { Observable } from 'rxjs';
import { Subject } from 'rxjs/internal/Subject';
import { tap } from 'rxjs/operators';

export interface AvailableSkill {
    icon: Object;
    iconImage: string;
    isMycroftMade: boolean;
    isSystemSkill: boolean;
    marketCategory: string;
    name: string;
    summary: string;
    title: string;
    trigger: string;
}

export interface SkillCredits {
    name: string;
    github_id: string;
}

export interface SkillDetail {
    categories: string[];
    credits: SkillCredits[];
    description: string;
    icon: Object;
    iconImage: string;
    isSystemSkill: boolean;
    name: string;
    repositoryUrl: string;
    summary: string;
    title: string;
    triggers: string;
    worksOnKDE: boolean;
    worksOnMarkOne: boolean;
    worksOnMarkTwo: boolean;
    worksOnPicroft: boolean;
}

const availableSkillsUrl = '/api/skill/available';
const skillUrl = '/api/skill/detail/';
const searchQuery = '?search=';

@Injectable()
export class SkillsService {
    public availableSkills: AvailableSkill[];
    public isFiltered = new Subject<boolean>();

    constructor(private http: HttpClient) { }

    /**
     * API call to retrieve all the skills available to the user
     */
    getAvailableSkills(): Observable<AvailableSkill[]> {
        return this.http.get<AvailableSkill[]>(availableSkillsUrl).pipe(
            tap((skills) => { this.availableSkills = skills; })
        );
    }

    /**
     * Loop through the available skills to build a list of distinct categories.
     */
    getSkillCategories(): string[] {
        const orderedSkillCategories: string[] = [];
        const skillCategories: string[] = [];
        let systemCategoryFound = false;
        this.availableSkills.forEach(
            (skill) => {
                if (!skillCategories.includes(skill.marketCategory)) {
                    skillCategories.push(skill.marketCategory);
                }
            }
        );
        skillCategories.sort();

        // Make the 'System' category display last, if it exists
        skillCategories.forEach(
            category => {
                if (category === 'System') {
                    systemCategoryFound = true;
                } else {
                    orderedSkillCategories.push(category);
                }
            }
        );
        if (systemCategoryFound) {
            orderedSkillCategories.push('System');
        }

        return orderedSkillCategories;
    }

    /**
     * API call to retrieve detailed information about a specified skill.
     *
     * @param skillName: name of the skill to retrieve
     */
    getSkillById(skillName: string): Observable<SkillDetail> {
        return this.http.get<SkillDetail>(skillUrl + skillName);
    }

    /**
     *  API call to retrieve available skills that match the specified search term.
     *
     * @param searchTerm string used to search skills
     */
    searchSkills(searchTerm: string): Observable<AvailableSkill[]> {
        this.isFiltered.next(!!searchTerm);
        return this.http.get<AvailableSkill[]>(
            availableSkillsUrl + searchQuery + searchTerm
        );
    }
}
