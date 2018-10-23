import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';

import { Observable } from 'rxjs';
import { Subject } from "rxjs/internal/Subject";
import { tap } from "rxjs/operators";

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
    platforms: string[];
    repositoryUrl: string;
    summary: string;
    title: string;
    triggers: string;
}

const availableSkillsUrl = '/api/skill/available';
const skillUrl = '/api/skill/detail/';
const searchQuery = '?search=';

@Injectable()
export class SkillsService {
    public availableSkills: AvailableSkill[];
    public isFiltered = new Subject<boolean>();

    constructor(private http: HttpClient) { }

    getAvailableSkills(): Observable<AvailableSkill[]> {
        return this.http.get<AvailableSkill[]>(availableSkillsUrl).pipe(
            tap((skills) => {this.availableSkills = skills;})
        )
    }

    getSkillCategories(): string[] {
        let orderedSkillCategories: string[] = [],
            skillCategories: string[] = [],
            systemCategoryFound: boolean = false;
        this.availableSkills.forEach(
            (skill) => {
                if (!skillCategories.includes(skill.marketCategory)) {
                    skillCategories.push(skill.marketCategory);}
                }
        );
        skillCategories.sort();

        // Make the "System" category display last, if it exists
        skillCategories.forEach(
            category => {
                if (category === 'System') {
                    systemCategoryFound = true;
                } else {
                    orderedSkillCategories.push(category)
                }
            }
        );
        if (systemCategoryFound) {
            orderedSkillCategories.push('System')
        }

        return orderedSkillCategories;
    }

    getSkillById(skillName: string): Observable<SkillDetail> {
        return this.http.get<SkillDetail>(skillUrl + skillName)
    }

    searchSkills(searchTerm: string): Observable<AvailableSkill[]> {
        this.isFiltered.next(!!searchTerm);
        return this.http.get<AvailableSkill[]>(
            availableSkillsUrl + searchQuery + searchTerm
        )
    }
}
